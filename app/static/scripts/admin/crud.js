class Field{
    constructor({name, displayName, validator, defaultValue = null, changeable = true}){
        this.name = name
        this.displayName = displayName
        this.validator = validator
        this.default = defaultValue
        this.changeable = changeable
    }

    validate(value){
        return this.validator.validate(value)
    }
}

class Erreur{
    static INVALID_DATA_TYPE = 'INVALID_DATA_TYPE'
    static UNIQUE_CONSTRAINT_VIOLATION = 'UNIQUE_CONSTRAINT_VIOLATION'
    static MULTIPLE_UNIQUE_CONSTRAINT_VIOLATION = 'MULTIPLE_UNIQUE_CONSTRAINT_VIOLATION'
    static FOREIGN_KEY_CONSTRAINT_VIOLATION = 'FOREIGN_KEY_CONSTRAINT_VIOLATION'
    static MISSING_REQUIRED_FIELD = 'MISSING_REQUIRED_FIELD'
    static NOT_FOUND_ON_TWITCH = 'NOT_FOUND_ON_TWITCH'
    static SERVICE_UNAVAILIABLE = 'SERVICE_UNAVAILIABLE'
    static VALUE_NOT_ALLOWED = 'VALUE_NOT_ALLOWED'
    static MUTTIPLE_VALUE_NOT_ALLOWED = 'MUTTIPLE_VALUE_NOT_ALLOWED'
    static NOT_FOUND = 'NOT_FOUND'
    static message = {
        [Erreur.INVALID_DATA_TYPE]: 'Type de donnée invalide',
        [Erreur.UNIQUE_CONSTRAINT_VIOLATION]: 'Violation de contrainte d\'unicité',
        [Erreur.MULTIPLE_UNIQUE_CONSTRAINT_VIOLATION]: 'Violation de contrainte d\'unicité multiple',
        [Erreur.FOREIGN_KEY_CONSTRAINT_VIOLATION]: 'Violation de contrainte de clé étrangère',
        [Erreur.MISSING_REQUIRED_FIELD]: 'Champ requis manquant',
        [Erreur.NOT_FOUND_ON_TWITCH]: 'Introuvable sur Twitch',
        [Erreur.SERVICE_UNAVAILIABLE]: 'Service non disponible',
        [Erreur.VALUE_NOT_ALLOWED]: 'Valeur non autorisée',
        [Erreur.MUTTIPLE_VALUE_NOT_ALLOWED]: 'Valeur multiple non autorisée',
        [Erreur.NOT_FOUND]: 'Introuvable'
    }
}
class Validation{
    constructor({f_validate = (value)=>true, required = true, allowed_values = [], isMultiValue = false}){
        this.f_validate = f_validate
        this.required = required
        this.allowed_values = allowed_values
        this.isMultiValue = isMultiValue
    }

    validate(...values){
        const errorMessages = []
        for(let item of values){
            if(!item && this.required){
                errorMessages.push(Erreur.MISSING_REQUIRED_FIELD)
                continue
            }
            const allowed_values = this.allowed_values.map(value=>value[CRUD.__idSelector])
            if(item && allowed_values.length && !allowed_values.includes(item))  errorMessages.push(Erreur.VALUE_NOT_ALLOWED)
            if(!this.isMultiValue && values.length>1) errorMessages.push(Erreur.MUTTIPLE_VALUE_NOT_ALLOWED)
            if(!this.f_validate(item)){
                // errorMessages.push(Erreur.INVALID_DATA_TYPE)
            }
        }
        return errorMessages
    }
    static addFunction(function_name, func){
        this[function_name] = (value)=>func(value) && value
    }

    static isInteger(value){
        return !isNaN(parseInt(value,10)) && parseInt(value,10);
    }

    static isNumber(value){
        return !isNaN(parseFloat(value,10)) && parseFloat(value,10)
    }

    static isString(value){
        return value instanceof String && value;
    }
    static regex(value, regex){
        return Validation.isString(value) && value.match(regex) && value
    }

    static isArray(array, f_validateValue=(value)=>value){
        if(Array.isArray(array)){
            const new_array = []
            for(elem of array){
                new_array.push(f_validateValue(elem));
            }
            return new_array
        }
        return false
    }
}


class CRUD{
    static  __idSelector = 'id'
    static  __valueSelector = 'value'
    static toCheckboxList(list = [], idKey = 'id', valueKey = 'value'){
        const checkBoxList = []
        for(let item of list){
            let dict = {}
            dict[CRUD.__idSelector] = item[idKey]
            dict[CRUD.__valueSelector] = item[valueKey]
            checkBoxList.push(dict);
        }

        return checkBoxList
    }
    constructor(idContainer, title, baseURL, f_formatData, ...fields){
        this.__idContainer = idContainer
        this.__f_formatData = f_formatData
        this.__title = title
        this.__baseURL = baseURL 
        this.fields = fields
        this.__table = $('<table>')
        this.__table.addClass('crud')
        this.__thead = $('<thead>')
        this.__tbody = $('<tbody>') 
        this.renew()
    }
    validate(formData){
        const errors = {}
        for(let [name, value] of formData)
        {
            let field = this.fields.find(field=>field.name==name)
            if(!field) continue            
            let error = field.validate(value)
            if(error.length){
                errors[name] = error
            }
        }
        return errors
    }
    __createForm(id_item = null){
        const item = this.getOne(id_item)

        const rowCreate = $('<tr>')

        rowCreate.addClass(id_item? 'update_item': 'new_item')
        for(let field of this.fields){
            let td = $('<td>');
            if(field.validator.allowed_values.length){
                const inputContainer  = $('<div class="multichoice">');
                field.validator.allowed_values.forEach(value => {
                    const input = $('<input>').attr({
                        disabled: !field.changeable && id_item,
                        type: field.validator.isMultiValue ? 'checkbox' : 'radio',
                        name: field.name,
                        value: value[CRUD.__idSelector],
                        required: field.validator.required,
                        id:`CRUD_${value[CRUD.__valueSelector]}_${value[CRUD.__idSelector]}`,
                        checked: Boolean(item[field.name] && item[field.name].includes(value[CRUD.__valueSelector]))
                    });
                    const inputLabel = $('<label>').text(value[CRUD.__valueSelector]).attr({
                        for: `CRUD_${value[CRUD.__valueSelector]}_${value[CRUD.__idSelector]}`
                    });
                    inputContainer.append(input).append(inputLabel);
                    inputContainer.append(input);
                });
                inputContainer.appendTo(td)
            }
            else{
                const input = $('<input>')
                input.attr({
                    'name':field.name,
                    'value': item[field.name] || field.default,
                    'disabled': !field.changeable && id_item,
                })
                input.appendTo(td)
            }
            
            td.appendTo(rowCreate)
        }
        const confirmButton = $('<button>')
        .text('Valider')
        .attr({'type': 'submit', 'title': 'Valider'});
        const current_crud = this;
        confirmButton.on('click', function(even){
            even.preventDefault();
            const formData = new FormData();
            const form = $(`#${current_crud.__idContainer}`).get(0);            
            let elements = $(form);
            elements = id_item?elements.find('.update_item'):elements.find('.new_item')
            elements = elements.find('input, select, textarea');
            elements.each(function() {
                const element = $(this);
                if (element.is(':disabled')){
                    return
                }
                const name = element.attr('name');
                if (element.is('input[type="checkbox"]') || element.is('input[type="radio"]')) {
                    if(!formData.has(name)){
                        formData.append(name, '')
                    }
                    if (element.is(':checked')) {
                        if (!formData.get(name)) {
                            formData.set(name, element.val());
                        } else {
                            formData.append(name, element.val());
                        }
                    }
                }
                else if (element.is('select')) {
                    formData.append(name, element.find('option:selected').val());
                }
                else {   
                    formData.append(name, element.val());
                }
            });
            const errors = current_crud.validate(formData)
            if(Object.keys(errors).length){
                current_crud.createErrors(`#${current_crud.__idContainer} ${id_item?`.update_item`:`.new_item`}`, errors)
                return
            }
            if(id_item){
                return current_crud.updateItem(id_item,formData)
            }
            else{
                current_crud.createItem(formData)
            }
        })
        const cancelButton = $('<button>')
        .text('Annuler')
        .attr({'title': 'Annuler'});
        cancelButton.on('click', function(even){
            even.preventDefault();
            $(`#${current_crud.__idContainer}  .update_item`).remove()
            $(`#${current_crud.__idContainer}  #${id_item}`).show()
            $(`#${current_crud.__idContainer} button:contains('Modifier')`).attr('disabled',false);
        })
        let td = $('<td>');
        if(id_item){
            const buttons = $('<div>')
            buttons.append(cancelButton)
            buttons.append(confirmButton)
            buttons.appendTo(td)
            td.appendTo(rowCreate)
        }
        else{
            confirmButton.appendTo(td);
            td.appendTo(rowCreate)
        }

        return rowCreate
    }
    __createAddButton(){
        const addButton = $('<button>')
        addButton.text('Ajouter')
        addButton.attr('title', 'Ajouter')
        let state = 0;
        const current_crud = this 
        addButton.on('click', function(event) {
            event.preventDefault()
            state = (++state)%2
            if(state){
                $(this).text('Annuler')
                current_crud.__createForm().prependTo(current_crud.__tbody)
            }else{
                $(this).text('Ajouter')
                $(`#${current_crud.__idContainer}  .new_item`).remove()
            }
        });        
        return addButton
    }
    __createUpdateButton(){
        const editButton = $('<button>')
        editButton.text('Modifier')
        editButton.attr('title', 'Modifier')
        const current_crud = this
        editButton.on('click', function(event) {
            event.preventDefault()
            let id_item = $(this).closest('tr').attr('id')
            current_crud.__createForm(id_item).insertAfter($(`#${current_crud.__idContainer} #${id_item}`))
            $(`#${current_crud.__idContainer} button:contains('Modifier')`).attr('disabled',true);
            $(`#${current_crud.__idContainer} #${id_item}`).hide()
        });        
        return editButton
    }
    __createDeleteButton(){
        const deleteButton = $('<button>')
        deleteButton.text('Supprimer')
        deleteButton.attr('title', 'Supprimer')

        const current_crud = this 
        deleteButton.on('click', function(event) {
            event.preventDefault()
            if(confirm('Êtes-vous sûr de vouloir supprimer?')){
                let uuid = $(this).closest('tr').attr('id')
                current_crud.deleteItem(uuid)
            }
          });        
        return deleteButton
    }
    __displayCRUD(){
        const title = $('<th>');
        title.text(this.__title)
        title.attr('colspan', (this.fields).length+1)
        title.appendTo($('<tr>')).appendTo(this.__thead)
        const trHeader = $('<tr>');
        for(let field of this.fields){
            let th = $('<th>');
            th.text(field.displayName)
            th.appendTo(trHeader)
        }
        let th = $('<th>');
        const addButton = this.__createAddButton()
        addButton.appendTo(th);
        th.appendTo(trHeader);
        const form = $('<form>');
        trHeader.appendTo(this.__thead);
        this.__thead.appendTo(this.__table);
        this.__tbody.appendTo(this.__table);
        this.__table.appendTo(form);
        form.appendTo($(`#${this.__idContainer}`))
    }
    renew(){
        $(`#${this.__idContainer}`).empty()
        this.__thead.empty();
        this.__tbody.empty();
        this.__table.empty();
        this.__displayCRUD()
        this.fillData()
    }
    fillData(){
        $(`#${this.__idContainer} button`).attr('disabled',true)
        const headers = new Headers();
        headers.append('Authorization', getToken());
        const request = new Request(this.__baseURL, {
            method: 'GET',
            headers: headers
        });

        fetch(request).then(response => {
            if (response.ok) {
                return response.json();
            } else {
                $(`#${this.__idContainer} button`).attr('disabled',false)
                throw new Error('Erreur de réseau');
            }
        })
        .then((data)=>{
            const formatedData = this.__f_formatData(data);
            Object.entries(formatedData).forEach(entry => {
                const [key, value] = entry;
                const tr = $('<tr>').attr('id', key);
                for (let field of this.fields) {
                    let td = $('<td>');
                    if (Array.isArray(value[field.name])) {
                      
                        const select = $('<select>').attr({
                            readonly: true,
                            name:field.name
                        });
                        value[field.name].forEach(option => {
                            $('<option>').val(option).text(option).appendTo(select);
                        });
                        td.append(select);
                    } 
                    else {
                        const input = $('<input>').attr({
                            type: 'text',
                            readonly: true,
                            value: value[field.name],
                            name: field.name
                        });
                        td.append(input);
                    }
                    td.appendTo(tr);
                }
                const buttons = $('<div>')
                buttons.append(this.__createUpdateButton())
                buttons.append(this.__createDeleteButton())
                const td_buttons = $('<td>')
                buttons.appendTo(td_buttons)
                tr.append(td_buttons)
                tr.appendTo(this.__tbody);
            });
            $(`#${this.__idContainer} button`).attr('disabled',false)
        })
        
    }
    createErrors(selector, jsonErrors){
        for(let [name, errors] of Object.entries(jsonErrors)){
            let field = $(selector).find(`[name="${name}"]`)
            if(errors.length){
                field.addClass('erreur_CRUD')
                field.nextAll('.message_error').remove()
                for(let error of errors){
                    const message_error = $('<div>')
                    message_error.text(Erreur.message[error])
                    message_error.addClass('message_error')
                    field.after(message_error)
                }
            }
            else{
                field.removeClass('erreur_CRUD')
                field.nextAll('.message_error').remove()
            }
            field.on('click', function(){
                $(this).removeClass('erreur_CRUD')
                $(this).nextAll('.message_error').remove()
            })
        }
    }
    createItem(formData){
        const headers = new Headers();
        headers.append('Authorization', getToken());
        const request = new Request(this.__baseURL, {
            method: 'POST',
            body: formData,
            headers: headers
        });

        fetch(request).then(response => {
            if (response.ok) {
                this.renew()
            } else {
                return response.json();
            }
        })
        .then((data)=>{
            this.createErrors(`#${this.__idContainer} .new_item`,data.errors);
        })
        .catch(error => {
            console.error('Erreur lors de l\'envoi de la requête AJAX', error);
        });
    }
    updateItem(uuid,formData){
        const headers = new Headers();
        headers.append('Authorization', getToken());
        const request = new Request(`${this.__baseURL}/${uuid}`, {
            method: 'PATCH',
            body: formData,
            headers: headers
        });

        fetch(request).then(response => {
            if (response.ok) {
                this.renew()
                return false
            } else {
                return response.json();
            }
        })
        .then((data)=>{
            if(data){
                this.createErrors(`#${this.__idContainer} .update_item`,data.errors);
            }
        })
        .catch(error => {
            console.error('Erreur lors de l\'envoi de la requête AJAX', error);
        });
    }
    deleteItem(uuid){
        const headers = new Headers();
        headers.append('Authorization', getToken());
        const request = new Request(`${this.__baseURL}/${uuid}`, {
            method: 'DELETE',
            headers: headers
        });

        fetch(request).then(response => {
            if (response.ok) {
                this.renew()
            } else {
                return response.json();
            }
        })
        .then((data)=>{
            this.createErrors(`#${this.__idContainer} #${uuid}` ,data.errors);
        })
        .catch(error => {
            console.error('Erreur lors de l\'envoi de la requête AJAX', error);
        });
    }
    getOne(item_id){
        const formData = {};
        let item = $(`#${this.__idContainer} #${item_id}`)
        const elements = $(item).find('input, select, textarea');
        elements.each(function() {
            const element = $(this);
            const name = element.attr('name');
            let value;
    
            if (element.is('select')) {
                // tous les options du select
                value = value = element.find('option').map(function() { return $(this).val(); }).get();
            }
            else {
                value = element.val();
            }
            formData[name] = value;
        });
        return formData;
    }
}
