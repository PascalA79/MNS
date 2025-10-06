async function profile(pseudo, user_id){
    const streamersRequest = new Request('/api/streamers', {
        method: 'GET'
    });
    const rolesRequest = new Request('/api/roles', {
        method: 'GET'
    });
    let allStreamers = []
    let allRoles = []
    allStreamers = await fetch(streamersRequest)
    .then(response=>{
        return response.json()
    })
    .then(data=>{
        return DataFormator.convert_to_multivalue(data.streamers, 'streamer_id', 'pseudo')
    })

    allRoles = await fetch(rolesRequest)
    .then(response=>{
        return response.json()
    })
    .then(data=>{
        return DataFormator.convert_to_multivalue(data.roles, 'role_id', 'name')
    })

    const field_profile = [
        new Field({name:'pseudo', displayName:'Pseudo', changeable:false, validator: new Validation({required:true})}),
        new Field({name:'streamer', displayName:'Pseudo Twitch',changeable:true, validator: new Validation({required:false, allowed_values: {...allStreamers, Infinity}, is_multivalue:false})}),
        new Field({name:'roles', displayName:'Role', changeable:false, validator: new Validation({required:false, allowed_values: allRoles, is_multivalue:true})}),
        new Field({name:'new_password', displayName:'Mot de passe', changeable:true, validator: new Validation({required:false, type: Validation.Type.PASSWORD, f_validate: (value, form)=>{return form.confirm_password === value}, f_error: Erreur.SAME_VALUE_ONLY})}),
        new Field({name:'confirm_password', displayName:'Confirmer le mot de passe', changeable:true, validator: new Validation({required:false, type: Validation.Type.PASSWORD})}),
    ]
    const crud_profile = new Formulaire('profile', pseudo, `/api/users/${user_id}`,
    [Formulaire.Action.UPDATE, Formulaire.Action.READ], async function(data){
        this.state = this.state ? this.state : false
        if(this.state){
            const new_request = new Request('/api/streamers', {
                method: 'GET'
            });
            allStreamers = await fetch(new_request)
            .then(response=>{
                return response.json()
            })
            .then(data=>{
                return DataFormator.convert_to_multivalue(data.streamers, 'streamer_id', 'pseudo')
            })
            crud_profile.fields.find(field=>field.name=='streamer').validator.allowed_values = {...allStreamers, Infinity}
        }
        this.state = true
        let formated_data = [data.users]
        formated_data = DataFormator.join(formated_data, allRoles, data.user_roles, 'user_id', 'role_id', 'roles')
        DataFormator.join(formated_data, allStreamers, data.streamers, 'user_id', 'streamer_id', 'streamer')
        for(let user of formated_data){
            if(user.streamer.length > 0){
                user.streamer = user.streamer[0]
            }
            user.streamers = user.streamer ? [user.streamer] : []
        }
        
        let formated_user = DataFormator.reduce([data.users], 'user_id')

        return formated_user
    }, ...field_profile)
    // const crud_streamer = new Formulaire('', pseudo, '/api/streamers', [Formulaire.Action.READ], function(data){

    //     return data.streamers
    // }, new Field({name:'pseudo', displayName:'Pseudo', changeable:false, validator: new Validation({required:true, allowed_values: allStreamers, is_multivalue:true})}))
    crud_profile.start_partial_refresh(2000)
}
