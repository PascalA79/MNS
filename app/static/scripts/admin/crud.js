class Field{
    constructor({name, displayName, validator, defaultValue = null, changeable = true, placeholder = '', fillable = true}) {
        this.name = name
        this.displayName = displayName
        this.validator = validator
        this.default = defaultValue
        this.changeable = changeable
        this.placeholder = placeholder
        this.fillable = fillable
    }

    validate(value){
        return this.validator.validate(value)
    }
}

class DataFormator{
    static convert_to_multivalue(data = [], key, value){
        if (key === null) {
            return Object.entries(data).reduce((acc, [object_id, object]) => {
                acc[object_id] = object[value];
                return acc;
            }, {});
        }
        return data.reduce((acc, item) => 
            ({ ...acc, [item[key]]: item[value] }), {}
        );
    }

    static join(data = [], join_map = {}, join_table = {}, foreign_key, key_name, field_name) {
        const joinMap = {};
        let join_table_values = Object.values(join_table)
        for (const join_item of join_table_values) {
            const key = join_item[foreign_key];
            if (!joinMap[key]) {
                joinMap[key] = [];
            }
            joinMap[key].push(join_map[join_item[key_name]]);
        }
        for (const item of data) {
            item[field_name] = joinMap[item[foreign_key]] || [];
        }
    
        return data;
    }
    static replace(data = [], join_table = {}, foreign_key){
        data.forEach(item=>{
            item[foreign_key] = join_table[item[foreign_key]]
        })
        return data
    }
    static reduce(data = [], key){
        return data.reduce((acc, item) => 
            ({ ...acc, [item[key]]: item }), {}
        );
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
    static NOT_FOUND_ON_SMM2 = 'NOT_FOUND_ON_SMM2'
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
        [Erreur.NOT_FOUND]: 'Introuvable',
        [Erreur.NOT_FOUND_ON_SMM2]: 'Introuvable sur SMM2'
    }
}

class Validation{
    static Type = class{
        static INTEGER = 'INTEGER'
        static NUMBER = 'NUMBER'
        static STRING = 'STRING'
        static DATE = 'DATE'
        static DATE_TIME = 'DATE_TIME'
        static TIMER = 'TIMER'
        static toArray(){
            return Object.values(this)
        }
    }
    constructor({f_validate = (value)=>true, required = true, type = Validation.Type.STRING, allowed_values = null, is_multivalue = true}) {
        this.f_validate = f_validate
        this.required = required
        this.type = type
        this.allowed_values = allowed_values
        this.is_multivalue = is_multivalue
    }

    validate(...values){
        const errorMessages = []
        for(let item of values){
            if(!item && this.required){
                errorMessages.push(Erreur.MISSING_REQUIRED_FIELD)
                continue
            }
            if(this.multivalue){
                const allowed_values = this.multivalue.keys()
                if(item && allowed_values.length && !(allowed_values.includes(item) || allowed_values.includes(undefined)))  errorMessages.push(Erreur.VALUE_NOT_ALLOWED)
                if(!this.multivalue.is_multivalue && values.length>1) errorMessages.push(Erreur.MUTTIPLE_VALUE_NOT_ALLOWED)
            }
            if(!this.f_validate(item)){
                // errorMessages.push(Erreur.INVALID_DATA_TYPE)
            }
        }
        return errorMessages
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
    static isDate(value){
        return new Date(value) && value
    }

}

class CRUD{
    static Action = class{
        static CREATE = 'CREATE'
        static UPDATE = 'UPDATE'
        static DELETE = 'DELETE'
        static READ = 'READ'
        static READ_ACTION_REQUIRED_ERROR = class extends Error{
            constructor(message){
                super(message)
            }
        }
    }
    static Item = class{
        constructor({id, data}){
            this.id = id
            this.data = data
        }
    }
    #idContainer
    #f_formatData
    #title
    #baseURL
    #table
    #thead
    #tbody
    #is_create
    #is_read
    #is_update
    #is_delete
    #eTag
    #currents_data = {}
    constructor(idContainer, title, baseURL, actions, f_formatData, ...fields){
        this.#idContainer = idContainer
        this.#f_formatData = f_formatData
        this.#title = title
        this.#baseURL = baseURL 
        this.fields = fields
        this.#table = $('<table>')
        this.#table.addClass('crud')
        this.#thead = $('<thead>')
        this.#tbody = $('<tbody>')
        this.#is_create = actions.includes(CRUD.Action.CREATE);
        this.#is_read = actions.includes(CRUD.Action.READ);
        this.#is_update = actions.includes(CRUD.Action.UPDATE);
        this.#is_delete = actions.includes(CRUD.Action.DELETE);
        if (!this.#is_read && (this.#is_update || this.#is_delete)){
            this.#is_update = false
            this.#is_delete = false
            throw new CRUD.Action.READ_ACTION_REQUIRED_ERROR('READ action is required')
        }
        this.#eTag = null
        this.build()
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
    #createForm(id_item = null){
        const item = this.getOne(id_item)
        const rowCreate = $('<tr>')

        rowCreate.addClass(id_item? 'update_item': 'new_item')
        for(let field of this.fields){
            let td = $('<td>');
            let is_disabled = (id_item && !field.changeable) || (!id_item && !field.fillable);
            if(field.validator.allowed_values){
                const inputContainer  = $('<div class="multichoice">');
                Object.entries(field.validator.allowed_values).forEach(([key,value]) => {
                    let input;
                    if(false && value == Infinity){
                        input = $('<textarea>').attr({
                            disabled: is_disabled,
                            name: field.name,
                        }).css({
                            minWidth: '100%'
                        });
                    }
                    else{
                        input = $('<input>').attr({
                            disabled: is_disabled,
                            type: field.validator.is_multivalue ? 'checkbox' : 'radio',
                            name: field.name,
                            value: key,
                            required: field.validator.required,
                            id:`CRUD_${field.name}_${value}_${key}`,
                            checked: Boolean(item[field.name] && item[field.name].includes(value))
                        });
                        const inputLabel = $('<label>').text(value).attr({
                            for: `CRUD_${field.name}_${value}_${key}`
                        });
                        inputContainer.append(input).append(inputLabel);
                    }
                    inputContainer.append(input);
                });
                const ErraseButton = $('<button>').text('Effacer').attr('type', 'button');
                if(!field.validator.required){
                    ErraseButton.on('click', function(){
                        inputContainer.find('input').prop('checked', false);
                    });
                    ErraseButton.appendTo(inputContainer);
                }
                inputContainer.appendTo(td)
            }
            else if(field.validator.type == Validation.Type.DATE){
                const input = $('<input>').attr({
                    type: 'date',
                    name: field.name,
                    value: item[field.name] || field.default,
                    disabled: is_disabled
                });
                input.appendTo(td)
            }
            else if(field.validator.type == Validation.Type.DATE_TIME){
                const input = $('<input>').attr({
                    type: 'datetime-local',
                    name: field.name,
                    value: item[field.name] || field.default,
                    disabled: is_disabled
                });
                input.appendTo(td)
            }
            else if(field.validator.type == Validation.Type.TIMER){
                const intToTimer = ms => `${String(Math.floor(ms / 3600000)).padStart(2, '0')}:${String(Math.floor((ms % 3600000) / 60000)).padStart(2, '0')}:${String(Math.floor((ms % 60000) / 1000)).padStart(2, '0')}.${String(ms % 1000).padStart(3, '0')}`;
                const input = $('<input>').attr({
                    type: 'time',
                    name: field.name,
                    value: intToTimer(item[field.name] || field.default),
                    disabled: is_disabled,
                    step:"0.1"

                });
                input.appendTo(td)
            }
            else if(field.validator.type == Validation.Type.INTEGER){
                const input = $('<input>').attr({
                    type: 'number',
                    name: field.name,
                    value: item[field.name] || field.default,
                    disabled: is_disabled
                });
                input.appendTo(td)
            }
            else if(field.validator.type == Validation.Type.NUMBER){
                const input = $('<input>').attr({
                    type: 'number',
                    name: field.name,
                    value: item[field.name] || field.default,
                    disabled: is_disabled
                });
                input.appendTo(td)
            }
            else{
                const input = $('<input>')
                input.attr({
                    'name':field.name,
                    'value': item[field.name] || field.default,
                    'disabled': is_disabled
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
            const form = $(`#${current_crud.#idContainer}`).get(0);            
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
                current_crud.createErrors(`#${current_crud.#idContainer} ${id_item?`.update_item`:`.new_item`}`, errors)
                return
            }
            const data = {}
            for (let pair of formData.entries()) {
                if (!data[pair[0]]) {
                    data[pair[0]] = [];
                }
                data[pair[0]].push(pair[1]);
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
            $(`#${current_crud.#idContainer}  .update_item`).remove()
            $(`#${current_crud.#idContainer}  #${id_item}`).show()
            $(`#${current_crud.#idContainer} button:contains('Modifier')`).attr('disabled',false);
        })
        let td = $('<td>');
        const buttons = $('<div>')
        if(id_item) buttons.append(cancelButton)
        buttons.append(confirmButton)
        buttons.appendTo(td)
        td.appendTo(rowCreate)
        return rowCreate
    }
    #createAddButton(){
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
                current_crud.#createForm().prependTo(current_crud.#tbody)
            }else{
                $(this).text('Ajouter')
                $(`#${current_crud.#idContainer}  .new_item`).remove()
            }
        });        
        return addButton
    }
    #createUpdateButton(){
        const editButton = $('<button>')
        editButton.text('Modifier')
        editButton.attr('title', 'Modifier')
        const current_crud = this
        editButton.on('click', function(event) {
            event.preventDefault()
            let id_item = $(this).closest('tr').attr('id')
            current_crud.#createForm(id_item).insertAfter($(`#${current_crud.#idContainer} #${id_item}`))
            $(`#${current_crud.#idContainer} button:contains('Modifier')`).attr('disabled',true);
            $(`#${current_crud.#idContainer} #${id_item}`).hide()
        });        
        return editButton
    }
    #createDeleteButton(){
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
    #displayCRUD(){
        const title = $('<th>');
        const extra_th = +(this.#is_update || this.#is_delete || this.#is_create)
        title.text(this.#title)
        title.attr('colspan', (this.fields).length+extra_th)
        title.appendTo($('<tr>')).appendTo(this.#thead)
        const trHeader = $('<tr>');
        for(let field of this.fields){
            let th = $('<th>');
            th.text(field.displayName)
            th.appendTo(trHeader)
        }
        if(extra_th){
            let th = $('<th>');
            if(this.#is_create){
                const addButton = this.#createAddButton()
                const container = $('<div>')
                container.append(addButton)
                container.appendTo(th)

            }
            th.appendTo(trHeader);
        }
        const form = $('<form>');
        trHeader.appendTo(this.#thead);
        this.#thead.appendTo(this.#table);
        this.#tbody.appendTo(this.#table);
        if(!$(`#${this.#idContainer}`).find('form').length){
            this.#table.appendTo(form);
            form.appendTo($(`#${this.#idContainer}`))
        }
    }
    #createRow(key, value, extra_td=null){
        const tr = $('<tr>').attr('id', key);
        for (let field of this.fields) {
            let td = $('<td>');
            if (Array.isArray(value[field.name]) && value[field.name].length) {
                const select = $('<select>').attr({
                    readonly: true,
                    name: field.name
                });
                value[field.name].forEach(option => {
                    $('<option>').val(option).text(option).appendTo(select);
                });
                td.append(select);
            } else if (field.validator.type == Validation.Type.TIMER) {
                const intToTimer = ms => `${String(Math.floor(ms / 3600000)).padStart(2, '0')}:${String(Math.floor((ms % 3600000) / 60000)).padStart(2, '0')}:${String(Math.floor((ms % 60000) / 1000)).padStart(2, '0')}.${String(ms % 1000).padStart(3, '0')}`;
                const input = $('<input>').attr({
                    type: 'time',
                    readonly: true,
                    value: intToTimer(value[field.name]),
                    name: field.name,
                    step: '0.1'
                });
                td.append(input);
            } else {
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
        if(extra_td){
            const buttons = $('<div>')
            if(this.#is_update) buttons.append(this.#createUpdateButton())
            if(this.#is_delete) buttons.append(this.#createDeleteButton())
            const td_buttons = $('<td>')
            buttons.appendTo(td_buttons)
            tr.append(td_buttons)
        }
        return tr;
    }
    build(){
        $(`#${this.#idContainer}`).empty()
        this.#thead.empty();
        this.#tbody.empty();
        this.#table.empty();
        this.#displayCRUD()
        this.updateData()
    }
    updateData(){
        if(!this.#is_read && this.#is_create){
            this.#createForm().appendTo(this.#tbody)
            return
        }
        const extra_td = +(this.#is_update || this.#is_delete || this.#is_create)
        const headers = new Headers();
        headers.append('Authorization', getToken());
        const request = new Request(this.#baseURL, {
            method: 'GET',
            headers: headers
        });

        fetch(request).then(response => {
            if (response.ok) {
                this.#eTag = response.headers.get('eTag')
                return response.json();
            } else {
                // $(`#${this.#idContainer} button`).attr('disabled',false)
                throw new Error('Erreur de réseau');
            }
        })
        .then((data)=>{
            const formatedData = this.#f_formatData(data);
            Object.entries(formatedData).forEach(entry => {
                const [key, value] = entry;
                let tr = null;
                if(key in this.#currents_data){
                    if(JSON.stringify(this.#currents_data[key]) == JSON.stringify(value)){
                        delete this.#currents_data[key]
                        return
                    }
                    else if($(`#${this.#idContainer} #${key}:not(.update_item)`).length){  
                        tr = this.#createRow(key, value, extra_td) 
                        $(`#${this.#idContainer} #${key}`).replaceWith(tr)
                    }
                    else{
                        $(`#${this.#idContainer} #${key}`).remove()
                    }
                    delete this.#currents_data[key]
                }
                if(!tr){
                    tr = this.#createRow(key, value, extra_td)
                    tr.appendTo(this.#tbody)
                }
            });
            for(let key in this.#currents_data){
                $(`#${this.#idContainer} #${key}`).remove()
            }
            this.#currents_data = formatedData
            $(`#${this.#idContainer} button`).attr('disabled',false)
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
        const request = new Request(this.#baseURL, {
            method: 'POST',
            body: formData,
            headers: headers
        });

        fetch(request).then(response => {
            if (response.ok) {
                $(`#${this.#idContainer} .new_item`).remove()
                this.updateData()
                this.#thead.empty();
                this.#displayCRUD();
                return false
            } else {
                return response.json();
            }
        })
        .then((data)=>{
            let errors = {}
            if(data){
                errors = data.errors
            }
            this.createErrors(`#${this.#idContainer} .new_item`,errors);
        })
        .catch(error => {
            console.error('Erreur lors de l\'envoi de la requête AJAX', error);
        });
    }
    updateItem(uuid,formData){
        const headers = new Headers();
        headers.append('Authorization', getToken());
        const request = new Request(`${this.#baseURL}/${uuid}`, {
            method: 'PATCH',
            body: formData,
            headers: headers
        });

        fetch(request).then(response => {
            if (response.ok) {
                this.updateData()
                $(`#${this.#idContainer} .update_item`).remove()
                return false
            } else {
                return response.json();
            }
        })
        .then((data)=>{
            if(data){
                this.createErrors(`#${this.#idContainer} .update_item`,data.errors);
            }
        })
        .catch(error => {
            console.error('Erreur lors de l\'envoi de la requête AJAX', error);
        });
    }
    deleteItem(uuid){
        const headers = new Headers();
        headers.append('Authorization', getToken());
        const request = new Request(`${this.#baseURL}/${uuid}`, {
            method: 'DELETE',
            headers: headers
        });

        fetch(request).then(response => {
            if (response.ok) {
                this.updateData()
            } else {
                return response.json();
            }
        })
        .then((data)=>{
            let errors = {}
            if(data){
                errors = data.errors
            }
            this.createErrors(`#${this.#idContainer} #${uuid}` , errors);
        })
        .catch(error => {
            console.error('Erreur lors de l\'envoi de la requête AJAX', error);
        });
    }
    getOne(item_id){
        return this.#currents_data[item_id] || {};
    }
    is_editited(){
        return $(`.crud .new_item`).length || $(`.crud .update_item`).length
    }
    start_partial_refresh(){
        setInterval(()=>{
            if (this.is_editited()) {
                return
            }
            fetch(this.#baseURL, {
                method: 'HEAD',
                headers: {
                    'Authorization': getToken(),
                    'eTag': this.#eTag
                }
            }).then(response => {
                if (response.ok) {
                    return response.headers.get('eTag');
                } else {
                    throw new Error('Erreur de réseau');
                }
            })
            .then((eTag)=>{
                if(this.#eTag != eTag){
                    this.#eTag = eTag
                    if(this.is_editited()){
                        return
                    }
                    this.updateData()
                }
            })
            .catch(error => {
                console.error(error);
            });
        }, 2000)
    }

}
