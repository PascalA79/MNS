async function createAdminPannel(){
    let allRoles = []
    let allStreamers = []
    let allGames = []
    let allUsers = []
    let allLevels = []
    let allEvents = []
    let allPlayers = []


    const eventsRequest = new Request('/api/events', {
        method: 'GET'
    });
    await fetch(eventsRequest)
    .then(response=>{
        return response.json()
    })
    .then(data => {
        allEvents = DataFormator.convert_to_multivalue(data.events, 'event_id', 'name');
        allPlayers = DataFormator.convert_to_multivalue(data.players, null, 'pseudo');
    })
    const levelsRequest = new Request('/api/events/levels', {
        method: 'GET'
    });
    allLevels = await fetch(levelsRequest)
    .then(response=>{
        return response.json()
    })
    .then(data=>{
        return DataFormator.convert_to_multivalue(data.levels, 'level_id', 'code')
    })
    
    const rolesRequest = new Request('/api/roles', {
        method: 'GET'
    });
    allRoles = await fetch(rolesRequest)
    .then(response=>{
        return response.json()
    })
    .then(data=>{
        return DataFormator.convert_to_multivalue(data.roles, 'role_id', 'name')
    })

    const streamersRequest = new Request('/api/streamers', {
        method: 'GET'
    });
    allStreamers = await fetch(streamersRequest)
    .then(response=>{
        return response.json()
    })
    .then(data=>{
        return DataFormator.convert_to_multivalue(data.streamers, 'streamer_id', 'pseudo')
    })
    const gamesRequest = new Request('/api/games', {
        method: 'GET'
    });
    allGames = await fetch(gamesRequest)
    .then(response=>{
        return response.json()
    })
    .then(data=>{
        return DataFormator.convert_to_multivalue(data.games, 'game_id', 'name')
    })

    const usersRequest = new Request('/api/users', {
        method: 'GET'
    });
    allUsers = await fetch(usersRequest)
    .then(response=>{
        return response.json()
    })
    .then(data=>{
        return DataFormator.convert_to_multivalue(data.users, 'user_id', 'pseudo')
    })

    const fields_levels = [
        new Field({name: 'name', displayName: 'Name', fillable:false, changeable: false, validator: new Validation({ required: false })}),
        new Field({name: 'code', displayName: 'Code', changeable: false, validator: new Validation({ required: true, f_validate: (value) => Validation.regex(value, /^(?=.{9}$|(?=.{11}$))[A-Za-z0-9]{3}-?[A-Za-z0-9]{3}-?[A-Za-z0-9]{3}$/) })}),
        new Field({name: 'creator', displayName: 'Creator', fillable:false, changeable: false, validator: new Validation({ required: false })}),
        new Field({name: 'description', displayName: 'Description', fillable:false, changeable: false, validator: new Validation({ required: false })}),
    ];

    const fields_event = [
        new Field({name:'name',displayName:'Name',changeable:true, validator: new Validation({ required:true, f_validate: (value)=>Validation.regex(value, /^[a-zA-Z0-9_]+$/)})}),
        new Field({name:'description', displayName:'Description',changeable:true, validator: new Validation({ required:true})}),
        new Field({name:'start_date',displayName:'Début',changeable:true, validator: new Validation({ required:true, type: Validation.Type.DATE_TIME})}),
        new Field({name:'user_id', displayName:'Organisateur',changeable:true, validator: new Validation({required:true, allowed_values: allUsers, is_multivalue:false})}),
        new Field({name:'levels', displayName:'Niveaux',changeable:true, validator: new Validation({required:false, allowed_values:allLevels, is_multivalue:true/*[...allLevels, Infinity]*/})}),
        new Field({name:'players', displayName:'Participants', changeable:true, validator:new Validation({required:false, allowed_values:allUsers, is_multivalue:true})})
    ]

    const fields_streamers = [
        new Field({name:'pseudo', displayName:'Pseudo',changeable:false, validator: new Validation({ required:true, f_validate: (value)=>Validation.regex(value, /^[a-zA-Z0-9_]+$/)})}),
        new Field({name:'id_twitch', displayName:'Twitch ID',changeable:false, fillable:false, validator: new Validation({required:false})})
    ];
    const fields_users = [
        new Field({name:'pseudo', displayName:'Pseudo', validator: new Validation({ required:true, f_validate: (value)=>Validation.regex(value, /^[a-zA-Z0-9_]+$/)})}),
        new Field({name:'password', displayName:'Mot de passe', changeable:false, validator: new Validation({required:true, f_validate: (value)=>Validation.regex(/^\S*$/)})}),
        new Field({name:'roles', displayName:'Roles', validator: new Validation({required:false,  allowed_values:allRoles, is_multivalue:true})}),
        new Field({name:'streamer', displayName:'Streamer',changeable:true, validator: new Validation({required:false, allowed_values: allStreamers, is_multivalue:false})})
    ];
    const fields_roles = [
        new Field({name:'name', displayName:'Nom',  validator: new Validation({ required:true, f_validate: (value)=>Validation.regex(value, /^[a-zA-Z0-9_]+$/)})})
    ]
    const fields_discord = [
        new Field({name:'name', displayName:'Nom', changeable:true, validator: new Validation({required:true})}),
        new Field({name:'id_guild', displayName:'Guild ID', changeable:true, validator: new Validation({required:true})}),
        new Field({name:'id_channel', displayName:'Channel ID', changeable:true, validator: new Validation({required:true})}),
        new Field({name:'games', displayName:'Games', validator: new Validation({required:false,  allowed_values:allGames, is_multivalue:true})}),
        new Field({name:'streamers', displayName:'Streamers', validator: new Validation({required:false, allowed_values:allStreamers, is_multivalue:true})})
    ]
    const fields_games = [
        new Field({name:'name', displayName:'Nom', changeable:false, validator: new Validation({required:true})}),
        new Field({name:'id_twitch', displayName:'Twitch ID', changeable:false, validator: new Validation({required:false})})
    ]
    const fields_timer = [
        new Field({name:'event_id', displayName:'Event', changeable:false, validator: new Validation({required:true, allowed_values:allEvents, is_multivalue:false})}),
        new Field({name : 'player_id',displayName: 'Pseudo', changeable:false, validator: new Validation({required:true, allowed_values:allUsers, is_multivalue:false})}),
        new Field({name : 'level_id',displayName: 'Niveau', changeable:false, validator: new Validation({required:true, allowed_values:allLevels, is_multivalue:false})}),
        new Field({name:'timer', displayName:'Timer', changeable:true, validator: new Validation({required:true, type: Validation.Type.TIMER})})
    ]
    
    const crud_discord = new CRUD('discord_app', 'Discord','/api/discord/guild',
        [CRUD.Action.DELETE, CRUD.Action.UPDATE, CRUD.Action.CREATE, CRUD.Action.READ], function(data){
        let formated_data_game = DataFormator.join(data.guilds, allGames, data.games, 'discord_id', 'game_id', 'games')
        let formated_data_streamer = DataFormator.join(formated_data_game, allStreamers, data.streamers, 'discord_id', 'streamer_id', 'streamers')
        return DataFormator.reduce(formated_data_streamer, 'discord_id')
    }, ...fields_discord)
    const crud_streamer = new CRUD('streamers', 'Streamers','/api/streamers',
        [CRUD.Action.DELETE, CRUD.Action.UPDATE, CRUD.Action.CREATE, CRUD.Action.READ], function(data){
        this.state = this.state ? this.state : false
        if(this.state){
            allStreamers = DataFormator.convert_to_multivalue(data.streamers, 'streamer_id', 'pseudo')
            crud_user.fields.find(field=>field.name=='streamer').validator.allowed_values = allStreamers
            crud_discord.fields.find(field=>field.name=='streamers').validator.allowed_values = allStreamers
            crud_discord.updateData()
            crud_user.updateData()
        }
        this.state = true
        return DataFormator.reduce(data.streamers, 'streamer_id')
    }, ...fields_streamers)
    const crud_event = new CRUD('events', 'Events', '/api/events',
        [CRUD.Action.UPDATE, CRUD.Action.CREATE, CRUD.Action.READ],
        function(data){
        this.state = this.state ? this.state : false 
        let formated_data_level = DataFormator.join(data.events, allLevels, data.event_levels, 'event_id', 'level_id', 'levels')
        DataFormator.replace(formated_data_level, allUsers, 'user_id')
        allEvents = DataFormator.convert_to_multivalue(data.events, 'event_id', 'name')
        let formated_data_player = DataFormator.join(formated_data_level, allUsers, data.players, 'event_id', 'user_id', 'players')
        if(this.state){
            allPlayers = DataFormator.convert_to_multivalue(data.players, null, 'pseudo')
            crud_timers.fields.find(field=>field.name=='player_id').validator.allowed_values = allUsers
            crud_timers.fields.find(field=>field.name=='event_id').validator.allowed_values = allEvents
            crud_timers.updateData()
        }
        this.state = true
        return DataFormator.reduce(formated_data_player, 'event_id')
    }, ...fields_event)
    const crud_timers = new CRUD('timers', 'Timers', '/api/events/timers',
        [CRUD.Action.DELETE, CRUD.Action.UPDATE, CRUD.Action.READ], function(data){
        DataFormator.replace(data.timers, allEvents, 'event_id')
        DataFormator.replace(data.timers, allLevels, 'level_id')
        DataFormator.replace(data.timers, allPlayers, 'player_id')

        return DataFormator.reduce(data.timers, 'timer_id')
    },
    ...fields_timer)
    const crud_game = new CRUD('games', 'Games','/api/games',
        [CRUD.Action.DELETE, CRUD.Action.UPDATE, CRUD.Action.CREATE, CRUD.Action.READ], function(data){
        this.state = this.state ? this.state : false
        if(this.state){
            allGames = DataFormator.convert_to_multivalue(data.games, 'game_id', 'name')
            crud_discord.fields.find(field=>field.name=='games').validator.allowed_values = allGames
            crud_discord.updateData()
        }
        this.state = true
        return DataFormator.reduce(data.games, 'game_id')
    }, ...fields_games)
    const crud_user = new CRUD('users', 'Users','/api/users',
        [CRUD.Action.DELETE, CRUD.Action.UPDATE, CRUD.Action.CREATE, CRUD.Action.READ], function(data){
        this.state = this.state ? this.state : false
        let formated_data_role = DataFormator.join(data.users, allRoles, data.user_roles, 'user_id', 'role_id', 'roles')
        DataFormator.join(formated_data_role, allStreamers, data.streamers, 'user_id', 'streamer_id', 'streamer')
        for(let user of formated_data_role){
            if(user.streamer.length > 0){
                user.streamer = user.streamer[0]
            }
            user.streamers = user.streamer ? [user.streamer] : []
        }
        if(this.state){
            allUsers = DataFormator.convert_to_multivalue(data.users, 'user_id', 'pseudo')
            crud_user.fields.find(field=>field.name=='roles').validator.allowed_values = allRoles
            crud_event.fields.find(field=>field.name=='user_id').validator.allowed_values = allUsers
            crud_event.fields.find(field=>field.name=='players').validator.allowed_values = allUsers
            crud_timers.fields.find(field=>field.name=='player_id').validator.allowed_values = allUsers
            crud_event.updateData()
            crud_timers.updateData()

        }
        this.state = true
        return DataFormator.reduce(formated_data_role, 'user_id')
    }, ...fields_users)
    const crud_role = new CRUD('roles', 'Roles','/api/roles',
        [CRUD.Action.DELETE, CRUD.Action.UPDATE, CRUD.Action.CREATE, CRUD.Action.READ], function(data){
        this.state = this.state ? this.state : false 
        if(this.state){
            allRoles = DataFormator.convert_to_multivalue(data.roles, 'role_id', 'name')
            crud_user.fields.find(field=>field.name=='roles').validator.allowed_values = allRoles
            crud_user.updateData()
        }
        this.state = true
        return DataFormator.reduce(data.roles, 'role_id')
    }, ...fields_roles)


    const crud_level = new CRUD('levels', 'Levels', '/api/events/levels',
        [CRUD.Action.DELETE, CRUD.Action.CREATE, CRUD.Action.READ], function(data){
        this.state = this.state ? this.state : false

        if(this.state){
            allLevels = DataFormator.convert_to_multivalue(data.levels, 'level_id', 'code')
            crud_event.fields.find(field=>field.name=='levels').validator.allowed_values = allLevels
            crud_event.updateData()
        }
        this.state = true
        return DataFormator.reduce(data.levels, 'level_id')
    }, ...fields_levels)
    crud_event.start_partial_refresh()
    crud_timers.start_partial_refresh()
    crud_user.start_partial_refresh()
    crud_role.start_partial_refresh()
    crud_discord.start_partial_refresh()
    crud_streamer.start_partial_refresh()
    crud_game.start_partial_refresh()
    crud_level.start_partial_refresh()
}
