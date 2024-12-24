from flask import Blueprint, make_response, request
from app.models import Event, Level, User, EventLevel, db, Token, Player, PlayerTimer
from app.constants import ApiConstant
from utility import delete_keys, timer_to_int
import uuid
from datetime import datetime

event_blueprint = Blueprint('event', __name__, url_prefix='/api/events')

@event_blueprint.route('/<uuid:event_id>', methods=['GET'])
def getEvent(event_id:uuid):
    event = Event().getOne(event_id)
    if not event:
        return make_response(
            {
                'errors':{
                    'event_id':ApiConstant.Errors.NOT_FOUND
                },
                'status':False
            }, ApiConstant.Http.NOT_FOUND)
    
    users = {}
    levels = {}
    event_levels = {}
    players = {}
    
    user = event.user
    users.update(user.to_sub_resource())
    
    for event_level in event.event_levels:
        level = event_level.level
        levels.update(level.to_sub_resource())
        event_levels.update(event_level.to_sub_resource())
    
    for player in event.players:
        players.update(player.to_sub_resource())
    
    response = {
        'event': dict(event),
        'users': users,
        'levels': levels,
        'event_levels': event_levels,
        'players': players,
        'status': True
    }
    return make_response(response, ApiConstant.Http.OK, {'ETag': event.get_eTag()})

@event_blueprint.route('/', methods=['GET'])
def getEvents():
    event = Event()
    filters = request.args.to_dict()
    events = event.getAll(**filters)
    users = {}
    levels = {}
    event_levels = {}
    players = {}
    for event in events:
        user = event.user
        users.update(user.to_sub_resource())
        for event_level in event.event_levels:
            level = event_level.level
            levels.update(level.to_sub_resource())
            event_levels.update(event_level.to_sub_resource())
        for player in event.players:
            players.update(player.to_sub_resource())
    response = {
            'events': [dict(e) for e in events],
            'users' : users,
            'levels' : levels,
            'event_levels' : event_levels,
            'players' : players,
            'status': True
        }
    return make_response(response, ApiConstant.Http.OK, {'ETag': Event.get_eTag()})

@event_blueprint.route('/', methods=['HEAD'])
def headEvents():
    return make_response('', ApiConstant.Http.OK, {'ETag': Event.get_eTag()})

@event_blueprint.route('/', methods=['POST'])
def addEvent():
    token = request.cookies.get('token')
    registration = Token().getOne(token)
    if not registration.user.is_admin:
        return make_response(
            {
                'errors': {
                    'user_id': ApiConstant.Errors.FORBIDDEN
                },
                'status': False
            }, ApiConstant.Http.FORBIDDEN)

    data = dict(request.form)
    event = Event()
    errors = Event.create_api_errors()

    if 'user_id' in data:
        user = User().getOne(data.get('user_id'))
        if not user:
            errors['user_id'] = ApiConstant.Errors.NOT_FOUND
        else:
            data['user_id'] = user.id

    if 'start_date' in data:
        try:
            data['start_date'] = datetime.strptime(data['start_date'], '%Y-%m-%dT%H:%M')
        except ValueError as e:
            errors['start_date'] = ApiConstant.Errors.INVALID_DATA_TYPE

    new_event, errors = event.insert(data, errors)

    if errors:
        return make_response({'errors': errors, 'status': False}, ApiConstant.Http.BAD_REQUEST)

    try:
        event_level_model = EventLevel
        levels = request.form.getlist('levels')
        for level_id in levels:
            event_level, errors = event_level_model.insert(new_event.id_public, level_id)

        player_model = Player()
        players = request.form.getlist('players')
        for player_id in players:
            player, errors = player_model.insert(new_event.id_public, player_id)
        timer_model = PlayerTimer()
        for player in new_event.players:
            for event_level in new_event.event_levels:
                timer_model.insert(event_level.level.id_public, player.id_public)
    except Exception as e:
        db.session.rollback()
        new_event.delete(new_event.id_public)
        return make_response({'errors': errors, 'status': False}, ApiConstant.Http.BAD_REQUEST)

    if errors:
        for event_level in EventLevel.query.filter_by(event_id=new_event.id).all():
            db.session.delete(event_level)
        db.session.delete(new_event)
        db.session.commit()
        return make_response({'errors': errors, 'status': False}, ApiConstant.Http.BAD_REQUEST)

    return make_response({'event_id': new_event.id_public, 'status': True}, ApiConstant.Http.CREATED, {'ETag': new_event.get_eTag()})

@event_blueprint.route('/<uuid:event_id>', methods=['PATCH'])
def updateEvent(event_id:uuid):
    token = request.cookies.get('token')
    registration = Token().getOne(token)
    if not registration.user.is_admin:
        return make_response(
            {
                'errors': {
                    'user_id': ApiConstant.Errors.FORBIDDEN
                },
                'status': False
            }, ApiConstant.Http.FORBIDDEN)
    
    data = dict(request.form)
    event = Event()
    current_event = event.getOne(event_id)
    if not current_event:
        return make_response(
            {
                'errors': {
                    'event_id': ApiConstant.Errors.NOT_FOUND
                },
                'status': False
            }, ApiConstant.Http.NOT_FOUND)
    errors = Event.create_api_errors()

    if 'user_id' in data:
        user = User().getOne(data.get('user_id'))
        if not user:
            errors['user_id'] = ApiConstant.Errors.NOT_FOUND
        else:
            data['user_id'] = user.id

    if 'start_date' in data:
        try:
            data['start_date'] = datetime.strptime(data['start_date'], '%Y-%m-%dT%H:%M')
        except ValueError as e:
            errors['start_date'] = ApiConstant.Errors.INVALID_DATA_TYPE

    updated_event, errors = event.update(event_id, data, errors)

    if errors:
        return make_response({'errors': errors, 'status': False}, ApiConstant.Http.BAD_REQUEST)

    try:
        timer_model = PlayerTimer()
        event_level_model = EventLevel()
        current_event_levels = updated_event.event_levels
        current_event_levels = {event_level.level.id_public:event_level for event_level in current_event_levels}
        current_event_levels_ids = current_event_levels.keys()
        levels = request.form.getlist('levels')

        if data.get('levels', None):
            for level_id in levels:
                if level_id in current_event_levels_ids:
                    del current_event_levels[level_id]
                else:
                    event_level, errors = event_level_model.insert(updated_event.id_public, level_id, errors)
                    for player in updated_event.players:
                        timer_model.insert(level_id, player.id_public)

        for event_level_not_found in current_event_levels.values():
            for player in updated_event.players:
                timer_model.delete_where(player_id=player.id, level_id=event_level_not_found.level.id)
            event_level_model.delete(event_level_not_found.id_public)

        player_model = Player()
        current_players = updated_event.players
        current_players = {player.user.id_public:player for player in current_players}
        current_players_ids = current_players.keys()
        users = request.form.getlist('players')

        for user_id in users:
            if user_id in current_players_ids:
                del current_players[user_id]
            elif user_id:
                player, errors = player_model.insert(updated_event.id_public, user_id, errors)
                for event_level in updated_event.event_levels:
                    if errors: continue
                    timer, errors = timer_model.insert(event_level.level.id_public, player.id_public, errors)
        
        for player_not_found in current_players.values():
            for event_level in updated_event.event_levels:
                timer_model.delete_where(player_id=player_not_found.id)
            player_model.delete(player_not_found.id_public)

    except Exception as e:
        db.session.rollback()
        return make_response({'errors': errors, 'status': False}, ApiConstant.Http.BAD_REQUEST)

    if errors:
        db.session.rollback()
        return make_response({'errors': errors, 'status': False}, ApiConstant.Http.BAD_REQUEST)

    return make_response({'status': True}, ApiConstant.Http.OK, {'ETag': updated_event.get_eTag()})

@event_blueprint.route('/<uuid:event_id>', methods=['DELETE'])
def deleteEvent(event_id:uuid):
    event = Event().getOne(event_id)
    if not event:
        return make_response(
            {
                'errors':{
                    'event_id':ApiConstant.Errors.NOT_FOUND
                },
                'status':False
            }, ApiConstant.Http.NOT_FOUND)
    for player in event.players:
        PlayerTimer.delete_where(player_id=player.id)
        Player.delete(player.id_public)
    for event_level in event.event_levels:
        EventLevel.delete(event_level.id_public)
    result = Event.delete(event_id)
    return make_response({'status': result}, ApiConstant.Http.OK if result else ApiConstant.Http.NOT_FOUND, {'ETag': event.get_eTag()})

@event_blueprint.route('/levels',methods=['GET'])
def getLevels():
    levels = Level().getAll()
    levels_list = []
    for level in levels:
        level_dict = dict(level)
        level_dict['thumbnail_url_level'] = level_dict['thumbnail_url_level'].removeprefix('app/static')
        level_dict['thumbnail_url_creator'] = level_dict['thumbnail_url_creator'].removeprefix('app/static')
        levels_list.append(level_dict)
    result = {
        'levels': levels_list,
        'status': True,
    }
    return make_response(result, ApiConstant.Http.OK, {'ETag': Level.get_eTag()})

@event_blueprint.route('/levels', methods=['HEAD'])
def headLevels():
    return make_response('', ApiConstant.Http.OK, {'ETag': Level.get_eTag()})

@event_blueprint.route('/levels', methods=['POST'])
def createLevel():
    data = dict(request.form)
    level = Level()
    errors = Level.create_api_errors()
    new_level, errors = level.insert(data, errors)
    if errors:
        return make_response({'errors': errors, 'status':False}, ApiConstant.Http.BAD_REQUEST)
    return make_response({'level_id': new_level.id_public, 'status':True}, ApiConstant.Http.CREATED, {'ETag': new_level.get_eTag()})

@event_blueprint.route('/levels/<uuid:level_id>', methods=['DELETE'])
def deleteLevel(level_id:uuid):
    level = Level().getOne(level_id)
    if not level:
        return make_response(
            {
                'errors':{
                    'level_id':ApiConstant.Errors.NOT_FOUND
                },
                'status':False
            }, ApiConstant.Http.NOT_FOUND)
    PlayerTimer.delete_where(level_id=level.id)
    EventLevel.delete_where(level_id=level.id)
    result = Level.delete(level_id)
    return make_response({'status': result}, ApiConstant.Http.OK if result else ApiConstant.Http.NOT_FOUND, {'ETag': level.get_eTag()})

@event_blueprint.route('/timers', methods=['GET'])
def getEventsTimers():
    timers = PlayerTimer().getAll()
    players = {}
    levels = {}
    events= {}
    users = {}
    for timer in timers:
        player = timer.player
        level = timer.level
        players.update(player.to_sub_resource())
        users.update(player.user.to_sub_resource())
        levels.update(level.to_sub_resource())
        for event_level in level.event_levels:
            event = event_level.event
            events.update(event.to_sub_resource())
            users.update(event.user.to_sub_resource())
    all_timers = [dict(timer, timer=timer.timer if timer.timer else 0, event_id=timer.player.event.id_public) for timer in timers]
    all_timers.sort(key=lambda timer: timer['level_id'])
    all_timers.sort(key=lambda timer: timer['player_id'])
    all_timers.sort(key=lambda timer: timer['event_id'])
    result = {
        'timers': all_timers,
        'players': players,
        'levels': levels,
        'events': events,
        'users': users,
        'status': True,
    }
    return make_response(result, ApiConstant.Http.OK, {'ETag': PlayerTimer.get_eTag()})

@event_blueprint.route('/timers', methods=['HEAD'])
def headTimers():
    return make_response('', ApiConstant.Http.OK, {'ETag': PlayerTimer.get_eTag()})

@event_blueprint.route('/timers/<uuid:timer_id>', methods=['PATCH'])
def updateTimer(timer_id:uuid):
    data = dict(request.form)
    delete_keys(data, 'event_id', 'player_id', 'level_id')
    timer = PlayerTimer()
    current_timer = timer.getOne(timer_id)
    if not current_timer:
        return make_response(
            {
                'errors': {
                    'timer_id': ApiConstant.Errors.NOT_FOUND
                },
                'status': False
            }, ApiConstant.Http.NOT_FOUND)
    errors = PlayerTimer.create_api_errors()
    if 'timer' in data:
        data['timer'] = timer_to_int(data['timer'])
    updated_timer, errors = timer.update(timer_id, data, errors)
    if errors:
        return make_response({'errors': errors, 'status': False}, ApiConstant.Http.BAD_REQUEST)
    return make_response({'status': True}, ApiConstant.Http.OK, {'ETag': updated_timer.get_eTag()})

@event_blueprint.route('/timers/<uuid:timer_id>', methods=['DELETE'])
def deleteTimer(timer_id:uuid):
    timer = PlayerTimer().getOne(timer_id)
    if not timer:
        return make_response(
            {
                'errors':{
                    'timer_id':ApiConstant.Errors.NOT_FOUND
                },
                'status':False
            }, ApiConstant.Http.NOT_FOUND)
    data_timer_zero = {
        'timer': 0,
    }
    updated_timer, errors = PlayerTimer().update(timer_id, data_timer_zero)
    if errors:
        return make_response({'errors': errors, 'status': False}, ApiConstant.Http.BAD_REQUEST)
    return make_response({'status': True}, ApiConstant.Http.OK, {'ETag': timer.get_eTag()})
