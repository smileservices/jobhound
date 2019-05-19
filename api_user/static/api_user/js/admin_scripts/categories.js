var Categories = {
    cats: [],
    indexedCats: {},
    catPrefix: 'cat_',
    renderedCatsObj: {},
    container: {},
    templates: {},
    ajaxObj: {},
    alertObj: {},
    url: '',
    logLevel: 'debug',
    init: function (cats, container, formTemplateID, buttonsTemplateID, ajaxObj, alertObj, url) {
        /*
        * cats: array of categories
        * container: jquery obj container
        * */
        var self = this;
        self.cats = cats;
        self.container = container;
        self.ajaxObj = ajaxObj;
        self.alertObj = alertObj;
        self.templates = {
            'form': '#'+formTemplateID,
            'buttons': '#'+buttonsTemplateID
        };
        self.url = url;
        
        //render cats options
        $.each(self.cats, function (i, cat) {
            self.indexedCats[self.catPrefix+cat.id] = cat;
            if (cat.parent_id !== null) return;
            self.renderedCatsObj[self.catPrefix+cat.id] = self.__renderCatOption(cat.name, cat.id);
        });
        return self;
    },
    render: function () {
        /*
        * Render the existing categories and the add new cat form 
        * */        
        var self = this;
        var rendered = '';
        //clean up
        self.container.empty();
        //render existent categs
        $.each(self.indexedCats, function (i, cat) {
            rendered += self.__renderForm(cat);
        });
        //render new category form
        rendered += self.__renderForm({
            'id': 'new',
            'name': ''
        }, true);
        self.container.append(rendered);
        //add listeners
        self.container.find('.category_save').click(function (e) {
            e.preventDefault();
            var data = self.__getFormData($(this).parents('form.category'));
            if (data.id === 'new') {
                self.__saveAction(data);
            } else {
                self.__updateAction(data);
            }
        });
        self.container.find('.category_delete').click(function(e) {
            e.preventDefault();
            var data = self.__getFormData($(this).parents('form.category'));
            self.__deleteAction(data);
        });
        //add select2 listeners
        $('.select_parent').select2({
            placeholder: "Parent category",
            allowClear: true
        });
    },
    
    __getFormData: function(formObj) {
        return {
            'name': formObj.find('input[name="name"]').val(),
            'id': formObj.find('input[name="id"]').val(),
            'parent': formObj.find('select[name="parent"]').val()
        };
    },
    
    __saveAction: function(data) {
        var self = this;
        self.ajaxObj.send(self.url, 'POST', data, self.alertObj, function(response) {
            self.alertObj.showAlert(response.text, 'info', true, false);
            self.log(response);
            self.__registerNewCat(response.data);
            self.render();
        }, true)
    },
    
    __updateAction: function (data ){
      var self = this;
        self.ajaxObj.send(self.url+'/'+data.id, 'PATCH', data, self.alertObj, function(response) {
            self.alertObj.showAlert(response.text, 'info', true, false);
            self.log(response);
            self.__updateCat(response.data);
            self.render();
        }, true)
    },
    
    __deleteAction: function(data) {
        var self = this;
        self.ajaxObj.send(self.url+'/'+data.id, 'DELETE', data, self.alertObj, function(response) {
            self.alertObj.showAlert(response.text, 'info', true, false);
            self.log(response);
            self.__removeCat(response.data);
            self.render();
        }, true)
    },
    __registerNewCat: function(cat) {
        var self = this;
        self.indexedCats[self.catPrefix+cat.id] = cat;
        if (cat.parent_id === null) {
            self.renderedCatsObj[self.catPrefix + cat.id] = self.__renderCatOption(cat.name, cat.id);
        }
    },
    
    __updateCat: function (cat) {
        var self = this;
        self.renderedCatsObj[self.catPrefix+cat.id] = self.__renderCatOption(cat.name, cat.id);
        self.indexedCats[self.catPrefix+cat.id] = cat;
    },
    
    __removeCat: function (cat) {
        var self = this;
        delete self.renderedCatsObj[self.catPrefix+cat.id];
        delete self.indexedCats[self.catPrefix+cat.id];
    },
    
    __renderCatOption: function (name,id,selected=false) {
        var isSelected = selected && ' selected="selected"';
        return '<option value="'+id+'"'+isSelected+'>'+name+'</option>';
    },
    
    __renderCatsForCat: function(cat) {
        /*
        * Renders options for parent dropdown
        * Excludes categories with parents
        * */
        var self = this;
        var catsRend = '';
        $.each(self.renderedCatsObj, function (id, rendered) {
            if (id === self.catPrefix+cat.id) return;
            if (id === self.catPrefix+cat.parent_id) {
                var parentCat = self.indexedCats[self.catPrefix+cat.parent_id];
                rendered = self.__renderCatOption(parentCat.name,parentCat.id,true);
            }
            catsRend += rendered;
        });
        return catsRend;
    },
    
    __renderButtons: function(cat, newForm=false) {
        var self = this;
        var buttons = $('<div></div>');
        buttons.template({
            'id': cat.id,
        }, self.templates.buttons);
        if (newForm) {
            buttons.find('.category_save').text('Add New').val('create');
            buttons.find('.category_delete').remove();
        }
        return buttons.html();
    },
    
    __renderForm: function (cat, newForm=false) {
        var self = this;
        var rendObj = $('<div></div>');
        // remove from category list the one present and select the parent
        var catsRend = self.__renderCatsForCat(cat);
        // render buttons
        var rendButtons = self.__renderButtons(cat, newForm);
        rendObj.template({
            'id': cat.id,
            'name': cat.name,
            'cats': catsRend,
            'buttons': rendButtons
        }, self.templates.form);
        return rendObj.html();
    },
    
    log: function(output, level='log') {
        var self = this;
        if (self.logLevel) {
            window.console[level](output)
        }
    }
};
