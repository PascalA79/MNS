$('body').ready(function(){
    handleFormSubmit('loginForm', null,
        async response=>{
            response.json().then(data=>{
                let token = data.value
                if(token){
                    setToken(token)
                    document.location.assign('/user/index.html')
                }
            })
        },
        async response=>console.log(await response.json()));

})
