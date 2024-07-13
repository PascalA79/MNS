async function createAdminPannel(){
    let allRoles = []
    let allStreamers = []
    let allGames = []
    const rolesRequest = new Request('/api/roles', {
        method: 'GET'
    });
    allRoles = await fetch(rolesRequest)
    .then(response=>{
        return response.json()
    })
    .then(data=>{
        return CRUD.toCheckboxList(data.roles, 'role_id', 'name')
    })

    const streamersRequest = new Request('/api/streamers', {
        method: 'GET'
    });
    allStreamers = await fetch(streamersRequest)
    .then(response=>{
        return response.json()
    })
    .then(data=>{
        return CRUD.toCheckboxList(data.streamers, 'streamer_id', 'pseudo')
    })
    const gamesRequest = new Request('/api/games', {
        method: 'GET'
    });
    allGames = await fetch(gamesRequest)
    .then(response=>{
        return response.json()
    })
    .then(data=>{
        return CRUD.toCheckboxList(data.games, 'game_id', 'name')
    })
    const fields_streamers = [
        new Field({name:'pseudo', displayName:'Pseudo',changeable:false, validator: new Validation({ required:true, f_validate: (value)=>Validation.regex(value, /^[a-zA-Z0-9_]+$/)})}),
        new Field({name:'id_twitch', displayName:'Twitch ID',changeable:false, validator: new Validation({required:false})})
    ];
    const fields_users = [
        new Field({name:'pseudo', displayName:'Pseudo', validator: new Validation({ required:true, f_validate: (value)=>Validation.regex(value, /^[a-zA-Z0-9_]+$/)})}),
        new Field({name:'password', displayName:'Mot de passe', changeable:false, validator: new Validation({required:true, f_validate: (value)=>Validation.regex(/^\S*$/)})}),
        new Field({name:'roles', displayName:'Roles', validator: new Validation({required:false, isMultiValue:true, allowed_values:allRoles})}),
    ];
    const fields_roles = [
        new Field({name:'name', displayName:'Nom',  validator: new Validation({ required:true, f_validate: (value)=>Validation.regex(value, /^[a-zA-Z0-9_]+$/)})})
    ]
    const fields_discord = [
        new Field({name:'name', displayName:'Nom', changeable:true, validator: new Validation({required:true})}),
        new Field({name:'id_guild', displayName:'Guild ID', changeable:true, validator: new Validation({required:true})}),
        new Field({name:'id_channel', displayName:'Channel ID', changeable:true, validator: new Validation({required:true})}),
        new Field({name:'games', displayName:'Games', validator: new Validation({required:false, isMultiValue:true, allowed_values:allGames})}),
        new Field({name:'streamers', displayName:'Streamers', validator: new Validation({required:false, isMultiValue:true, allowed_values:allStreamers})})
    ]
    const fields_games = [
        new Field({name:'name', displayName:'Nom', changeable:false, validator: new Validation({required:true})}),
        new Field({name:'id_twitch', displayName:'Twitch ID', changeable:false, validator: new Validation({required:false})})
    ]
    
    const crud_discord = new CRUD('discord_app', 'Discord','/api/discord/guild',function(data){
        this.state = this.state ? this.state : false 
        const discordData = {}
        const steamerData = Object.values(data['streamers'])
        const discord_streamers = steamerData.reduce((streamers, { pseudo, discord_app_name }) => {
            streamers[discord_app_name] = streamers[discord_app_name] || [];
            streamers[discord_app_name].push(pseudo);
            return streamers;
        }, {});
        const gameData = Object.values(data['games'])
        const discord_games = gameData.reduce((games, { game_name, discord_app_name }) => {
            games[discord_app_name] = games[discord_app_name] || [];
            games[discord_app_name].push(game_name);
            return games;
        }, {});
        for(let item of data['guilds']){
            discordData[item['discord_app_id']] = {
                'name':item['name'],
                'id_guild':item['id_guild'],
                'id_channel':item['id_channel'],
                'streamers':discord_streamers[item['name']],
                'games':discord_games[item['name']]
            }
        }
        return discordData
    }, ...fields_discord)
    const crud_streamer = new CRUD('streamers', 'Streamers','/api/streamers',function(data){
        const streamerData = {}
        for(let item of data['streamers']){
            streamerData[item['streamer_id']] = item
        }
        allStreamers = streamerData
        if(this.state){
            const streamers = []
            for(let streamer of Object.values(allStreamers)){
                let dict = {}
                dict['id'] = streamer['streamer_id']
                dict['value'] = streamer['pseudo']
                streamers.push(dict)
            }
            crud_discord.fields.find(field=>field.name=='streamers').validator.allowed_values = streamers
            crud_discord.renew()
        }
        this.state = true
        return streamerData
    }, ...fields_streamers)
    const crud_game = new CRUD('games', 'Games','/api/games',function(data){
        const gameData = {}
        for(let item of data['games']){
            gameData[item['game_id']] = item
        }
        allGames = gameData
        if(this.state){
            const games = []
            for(let game of Object.values(allGames)){
                let dict = {}
                dict['id'] = game['game_id']
                dict['value'] = game['name']
                games.push(dict)
            }
            crud_discord.fields.find(field=>field.name=='games').validator.allowed_values = games
            crud_discord.renew()
        }
        this.state = true
        return gameData
    }, ...fields_games)
    const crud_user = new CRUD('users', 'Users','/api/users',function(data){
        const userData = {}
        const roleData = Object.values(data['user_roles'])
        const roles = roleData.reduce((user_role, { pseudo, role_name }) => {
            user_role[pseudo] = user_role[pseudo] || [];
            user_role[pseudo].push(role_name);
            return user_role;
        }, {});
        for(let item of data['users']){
            userData[item['user_id']] = {
                'pseudo':item['pseudo'],
                'roles':roles[item['pseudo']]
            }
        }
        return userData
    }, ...fields_users)
    const crud_role = new CRUD('roles', 'Roles','/api/roles',function(data){
        this.state = this.state ? this.state : false 
        const roleData = {}
        for(let item of data['roles']){
            roleData[item['role_id']] = item
        }
        allRoles = roleData
        if(this.state){
            const roles = []
            for(let role of Object.values(allRoles)){
                let dict = {}
                dict['id'] = role['role_id']
                dict['value'] = role['name']
                roles.push(dict)
            }
            crud_user.fields.find(field=>field.name=='roles').validator.allowed_values = roles
            crud_user.renew()
        }
        this.state = true
        return roleData
    }, ...fields_roles)
    
    
}
