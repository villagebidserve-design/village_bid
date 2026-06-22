"""
WebSocket consumers for real-time bidding using Django Channels
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class BiddingRoomConsumer(AsyncWebsocketConsumer):
    """Handle real-time bidding room connections and updates"""
    
    async def connect(self):
        """User joins a bidding room"""
        self.auction_id = self.scope['url_route']['kwargs']['auction_id']
        self.room_group_name = f'bidding_room_{self.auction_id}'
        self.user = self.scope['user']
        
        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Accept connection
        await self.accept()
        
        # Get or create anonymous bidder ID
        anonymous_id_data = await self.get_or_create_anonymous_id()
        
        # Get current bidding room data
        room_data = await self.get_room_data()
        
        # Send initial room state to user
        await self.send(text_data=json.dumps({
            'type': 'room_joined',
            'anonymous_id': anonymous_id_data['anonymous_id'],
            'room_data': room_data,
            'message': f'Welcome to bidding room! You are: {anonymous_id_data["anonymous_id"]}'
        }))
        
        # Notify others that a bidder joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'bidder_joined',
                'anonymous_id': anonymous_id_data['anonymous_id'],
            }
        )
        
        logger.info(f"User {self.user.username} joined bidding room {self.auction_id}")
    
    async def disconnect(self, close_code):
        """User leaves the bidding room"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Get user's anonymous ID
        anonymous_id = await self.get_user_anonymous_id()
        
        if anonymous_id:
            # Notify others that bidder left
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'bidder_left',
                    'anonymous_id': anonymous_id,
                }
            )
        
        logger.info(f"User {self.user.username} left bidding room {self.auction_id}")
    
    async def receive(self, text_data):
        """Handle incoming messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'place_bid':
                await self.handle_place_bid(data)
            elif message_type == 'get_bid_history':
                await self.handle_get_bid_history(data)
            elif message_type == 'get_room_data':
                await self.handle_get_room_data(data)
            else:
                await self.send_error('Unknown message type')
        
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON')
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send_error(f'Error: {str(e)}')
    
    async def handle_place_bid(self, data):
        """Handle bid placement"""
        bid_amount = data.get('amount')
        
        if not bid_amount:
            await self.send_error('Bid amount is required')
            return
        
        try:
            bid_amount = Decimal(str(bid_amount))
        except:
            await self.send_error('Invalid bid amount')
            return
        
        # Validate and place bid
        result = await self.validate_and_place_bid(bid_amount)
        
        if result['success']:
            # Broadcast new bid to all users in the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'new_bid',
                    'bid_data': result['bid_data'],
                }
            )
            
            # Send confirmation to bidder
            await self.send(text_data=json.dumps({
                'type': 'bid_accepted',
                'message': 'Your bid has been placed!',
                'bid_data': result['bid_data'],
            }))
        else:
            await self.send_error(result['message'])
    
    async def handle_get_bid_history(self, data):
        """Send recent bid history"""
        limit = data.get('limit', 20)
        bid_history = await self.get_bid_history(limit)
        
        await self.send(text_data=json.dumps({
            'type': 'bid_history',
            'bids': bid_history,
        }))
    
    async def handle_get_room_data(self, data):
        """Send current room data"""
        room_data = await self.get_room_data()
        
        await self.send(text_data=json.dumps({
            'type': 'room_data',
            'data': room_data,
        }))
    
    # ============ Event handlers from group sends ============
    
    async def new_bid(self, event):
        """Broadcast new bid to user"""
        await self.send(text_data=json.dumps({
            'type': 'new_bid',
            'bid_data': event['bid_data'],
        }))
    
    async def bidder_joined(self, event):
        """Notify user that a bidder joined"""
        await self.send(text_data=json.dumps({
            'type': 'bidder_joined',
            'anonymous_id': event['anonymous_id'],
        }))
    
    async def bidder_left(self, event):
        """Notify user that a bidder left"""
        await self.send(text_data=json.dumps({
            'type': 'bidder_left',
            'anonymous_id': event['anonymous_id'],
        }))
    
    async def auction_ending_soon(self, event):
        """Notify about auction ending soon"""
        await self.send(text_data=json.dumps({
            'type': 'auction_ending_soon',
            'message': event['message'],
            'time_remaining': event['time_remaining'],
        }))
    
    async def auction_ended(self, event):
        """Notify about auction end"""
        await self.send(text_data=json.dumps({
            'type': 'auction_ended',
            'winner_anonymous_id': event['winner_anonymous_id'],
            'winning_bid': float(event['winning_bid']),
        }))
    
    async def you_were_outbid(self, event):
        """Notify user they were outbid"""
        await self.send(text_data=json.dumps({
            'type': 'you_were_outbid',
            'message': 'You were outbid!',
            'new_highest_bid': float(event['new_highest_bid']),
            'outbid_by': event['outbid_by'],
        }))
    
    # ============ Database operations ============
    
    @database_sync_to_async
    def get_or_create_anonymous_id(self):
        """Get or create anonymous bidder ID for user in this auction"""
        from livebidding.models import AnonymousBidderId
        from auctions.models import Auction
        
        try:
            auction = Auction.objects.get(id=self.auction_id)
            
            # Try to get existing anonymous ID
            try:
                anon_id = AnonymousBidderId.objects.get(
                    user=self.user,
                    auction=auction
                )
                return {
                    'anonymous_id': anon_id.anonymous_id,
                    'distance_km': anon_id.distance_km,
                }
            except AnonymousBidderId.DoesNotExist:
                # Create new anonymous ID
                letter, number, anonymous_id = AnonymousBidderId.generate_anonymous_id(auction)
                
                # Calculate distance (stub for now)
                distance_km = await self.calculate_distance()
                
                anon_id = AnonymousBidderId.objects.create(
                    user=self.user,
                    auction=auction,
                    letter=letter,
                    number=number,
                    anonymous_id=anonymous_id,
                    distance_km=distance_km
                )
                
                return {
                    'anonymous_id': anon_id.anonymous_id,
                    'distance_km': anon_id.distance_km,
                }
        except Exception as e:
            logger.error(f"Error getting/creating anonymous ID: {str(e)}")
            return {
                'anonymous_id': 'Unknown',
                'distance_km': None,
            }
    
    @database_sync_to_async
    def get_user_anonymous_id(self):
        """Get user's anonymous ID in this auction"""
        from livebidding.models import AnonymousBidderId
        from auctions.models import Auction
        
        try:
            anon_id = AnonymousBidderId.objects.get(
                user=self.user,
                auction_id=self.auction_id
            )
            return anon_id.anonymous_id
        except:
            return None
    
    @database_sync_to_async
    def validate_and_place_bid(self, bid_amount):
        """Validate and place a bid"""
        from livebidding.models import BiddingRoom, BidAudit, AnonymousBidderId, AntiFraudLog
        from auctions.models import Auction
        from bids.models import Bid
        from django.conf import settings
        
        try:
            auction = Auction.objects.get(id=self.auction_id)
            bidding_room = BiddingRoom.objects.get(auction=auction)
            anon_id = AnonymousBidderId.objects.get(user=self.user, auction=auction)
            
            # Check if auction is active
            if not bidding_room.is_active:
                return {'success': False, 'message': 'Auction is not active'}
            
            if auction.status != 'active':
                return {'success': False, 'message': 'Auction has ended'}
            
            # Check if user is seller
            if self.user == auction.seller:
                # Log fraud attempt
                AntiFraudLog.objects.create(
                    user=self.user,
                    auction=auction,
                    fraud_type='self_bid',
                    description=f'Seller tried to bid on their own auction',
                    severity='high',
                    action_taken='Bid rejected'
                )
                return {'success': False, 'message': 'Sellers cannot bid on their own auctions'}
            
            # Validate bid amount
            current_price = bidding_room.highest_bid or auction.starting_price
            minimum_required = current_price + auction.minimum_bid_increment
            
            if bid_amount < minimum_required:
                return {
                    'success': False,
                    'message': f'Minimum bid must be ₹{minimum_required}'
                }
            
            # Check rate limiting
            from django.utils.timezone import now
            from datetime import timedelta
            recent_bids = BidAudit.objects.filter(
                user=self.user,
                auction=auction,
                created_at__gte=now() - timedelta(minutes=1)
            ).count()
            
            if recent_bids >= settings.RATE_LIMIT_BID_MAX_PER_MINUTE:
                AntiFraudLog.objects.create(
                    user=self.user,
                    auction=auction,
                    fraud_type='rate_limit',
                    description=f'User exceeded rate limit for bids',
                    severity='medium',
                    action_taken='Bid rejected'
                )
                return {'success': False, 'message': 'Too many bids. Please wait before placing another bid'}
            
            # Create audit log
            bid_audit = BidAudit.objects.create(
                auction=auction,
                user=self.user,
                anonymous_id=anon_id,
                amount=bid_amount,
                is_valid=True,
                status='active',
                ip_address=self.get_client_ip(),
            )
            
            # Update bidding room
            bidding_room.highest_bid = bid_amount
            bidding_room.highest_bidder = self.user
            bidding_room.total_bids += 1
            bidding_room.save()
            
            # Mark previous highest bid as outbid
            previous_highest = BidAudit.objects.filter(
                auction=auction,
                status='winning'
            ).exclude(id=bid_audit.id)
            
            for prev_bid in previous_highest:
                prev_bid.status = 'outbid'
                prev_bid.save()
            
            # Mark new bid as winning
            bid_audit.is_winning = True
            bid_audit.status = 'winning'
            bid_audit.save()
            
            return {
                'success': True,
                'message': 'Bid placed successfully',
                'bid_data': {
                    'anonymous_id': anon_id.anonymous_id,
                    'amount': float(bid_amount),
                    'time': bid_audit.created_at.isoformat(),
                }
            }
        
        except Auction.DoesNotExist:
            return {'success': False, 'message': 'Auction not found'}
        except BiddingRoom.DoesNotExist:
            return {'success': False, 'message': 'Bidding room not found'}
        except Exception as e:
            logger.error(f"Error placing bid: {str(e)}")
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    @database_sync_to_async
    def get_bid_history(self, limit=20):
        """Get recent bid history"""
        from livebidding.models import BidAudit
        from auctions.models import Auction
        
        try:
            auction = Auction.objects.get(id=self.auction_id)
            bids = BidAudit.objects.filter(
                auction=auction,
                is_valid=True
            ).select_related('anonymous_id').order_by('-created_at')[:limit]
            
            return [
                {
                    'anonymous_id': bid.anonymous_id.anonymous_id if bid.anonymous_id else 'Unknown',
                    'amount': float(bid.amount),
                    'time': bid.created_at.isoformat(),
                    'is_winning': bid.is_winning,
                }
                for bid in reversed(bids)
            ]
        except:
            return []
    
    @database_sync_to_async
    def get_room_data(self):
        """Get current bidding room data"""
        from livebidding.models import BiddingRoom
        from auctions.models import Auction
        
        try:
            auction = Auction.objects.get(id=self.auction_id)
            bidding_room = BiddingRoom.objects.get(auction=auction)
            
            return {
                'highest_bid': float(bidding_room.highest_bid) if bidding_room.highest_bid else float(auction.starting_price),
                'starting_price': float(auction.starting_price),
                'total_bids': bidding_room.total_bids,
                'unique_bidders': bidding_room.active_bidders.count(),
                'auction_end_time': auction.end_time.isoformat(),
            }
        except:
            return {}
    
    async def calculate_distance(self):
        """Calculate approximate distance between user and seller"""
        # Stub implementation - returns random distance for now
        # In production, calculate based on user profile location and seller location
        import random
        return random.randint(5, 100)
    
    def get_client_ip(self):
        """Get client IP address"""
        headers = dict(self.scope.get('headers', []))
        return headers.get(b'x-forwarded-for', b'').decode().split(',')[0].strip() or 'unknown'
    
    async def send_error(self, message):
        """Send error message to user"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message,
        }))
