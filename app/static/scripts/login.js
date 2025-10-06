$('body').ready(function(){
   login();

})
function login(){
    const fields_connection = [
        new Field({name:'pseudo', displayName:'Pseudo', changeable:true, validator: new Validation({required:true})}),
        new Field({name:'password', displayName:'Mot de passe', changeable:true, validator: new Validation({required:true, type: Validation.Type.PASSWORD})})
    ]
    const crud_connection = new Formulaire('connection', 'Connection', '/token',
        {[Formulaire.Action.CREATE]:(data)=>{
            data.then(token=>{
                if(token.value){
                    setToken(token.value)
                    document.location.assign('/user/index.html')
                }
            })
        }}, function(data){
        return data
    }, ...fields_connection)
}
