/*
 JS for FEDS projects.
 */

//Create a namespace object.
var Feds = {
    //Some constants.
    FEDS_MACHINE_NAME_PARAM: 'machine_name',
    FEDS_DETERMINING_VALUE_PARAM: 'determining_value',
    //Project id.
    projectId: false,
    //Values for each setting.
    settingsValues: {},
    //For testing the visibility of each setting.
    visibilityTesters: {},
    //Settings validators.
    validators: [],
    //Ajax URL for getting widget HTML.
    widgetUrl: '',
    //Ajax URL for saving a setting.
    saveSettingUrl: '',
    //Ajax URL to get setting display HTML.
    settingDisplayUrl: '',
    //Ajax URL to generate a data set.
    generateUrl: '',
    //Ajax URL to erase a data set archive file.
    deleteArchiveUrl: '',
    /**
     * Update the visibility of all settings displays.
      */
    updateSettingVisibility: function() {
        //Do a visibility test for all the settings.
        //dependentSetting: machine name of the setting that is
        //going to be hidden or not.
        $.each(Feds.visibilityTesters, function (dependentSetting, values) {
            var DISPLAY_SPEED = 'slow';
            var dependentDomObj = $('#' + dependentSetting);
            if (dependentDomObj.length === 0) {
                throw 'Dependent not found: ' + dependentSetting;
            }
            if (dependentDomObj.length > 1) {
                throw 'Dependent duplicate: ' + dependentSetting;
            }
            //Add a class to the dependent setting to show that it depends
            //on something else.
            $(dependentDomObj).closest('.feds-setting').addClass('feds-dependent-setting');
            //The setting that determines dependent obj's visibility.
            var determinerMachineName = values[Feds.FEDS_MACHINE_NAME_PARAM];
            //If the determiner has determiningValue, dep obj is visible
            var determiningValue = values[Feds.FEDS_DETERMINING_VALUE_PARAM];
            //What value does the determiner have now?
            var determinerCurrentValue = Feds.settingsValues[determinerMachineName];
            if (determiningValue === determinerCurrentValue) {
                $(dependentDomObj).closest('.feds-setting').show(DISPLAY_SPEED)
            }
            else {
                $(dependentDomObj).closest('.feds-setting').hide(DISPLAY_SPEED);
            }
        })
    },
    /**
     * Show a widget for a setting.
     * @param machine_name Machine name of the setting.
     */
    showWidget: function(machine_name) {
        $.ajax({
            type: 'POST',
            url: Feds.widgetUrl,
            data: {
                'projectid': Feds.projectId,
                'machinename': machine_name
            },
            dataType: 'json'
        }).done(function (data) {
            //XHR success.
            //Check the return data.
            if ( ! data.widgethtml ) {
                console.error("Bah! No widget HTML.");
            }
            if ( ! data.validators ) {
                console.error("Bah! No widget validators.");
            }
            if ( data.status !== 'ok'){
                console.log(data.status);
                return;
            }
            $('#feds-widget').html(data.widgethtml);
            Feds.validators = data.validators;
            $('#settings-modal-dialog').modal();
        }).fail(function (jqXHR, message) {
            console.error(message);
        });
    },
    //Data validator helper object.
    dataValidator: {
        errorMessages: '',
        //Show the general error message only one per set of validations,
        //no matter how many times it happens.
        shownGeneralError: false,
        /**
         * Check a value.
         *
         * @param testType Min/max.
         * @param testDataType Data type, e.g., int, date.
         * @param cutoffValue Value at which test fails.
         * @param valueToCheck The value to check.
         * @returns {boolean} Is valueToCheck OK?
         */
        check: function (testType, testDataType, cutoffValue, valueToCheck) {
            testDataType = testDataType.trim().toLowerCase();
            var inputTypeOk = true;
            var numericTypes = ['int', 'float', 'currency'];
            var typeIsNumeric = numericTypes.indexOf(testDataType) > -1;
            // MT bad for all data types.
            if (valueToCheck === '' || valueToCheck === null) {
                inputTypeOk = false;
            }
            else if (typeIsNumeric && isNaN(valueToCheck)) {
                inputTypeOk = false;
            }
            else if (testDataType === 'date') {
                if (! this.isValidDate(valueToCheck)) {
                    inputTypeOk = false;
                }
            }
            if (!inputTypeOk) {
                if (!this.shownGeneralError) {
                    this.errorMessages += "Sorry, invalid data.\n";
                    this.shownGeneralError = true;
                }
                return false;
            }
            //Convert to required type.
            if (testDataType === 'int') {
                valueToCheck = parseInt(valueToCheck);
                cutoffValue = parseInt(cutoffValue);
            }
            else if (testDataType === 'float') {
                valueToCheck = parseFloat(valueToCheck);
                cutoffValue = parseFloat(cutoffValue);
            }
            else if (testDataType === 'currency') {
                valueToCheck = parseFloat(valueToCheck);
                cutoffValue = parseFloat(cutoffValue);
            }
            else if (testDataType === 'date') {
                valueToCheck = new Date(valueToCheck);
                cutoffValue = new Date(cutoffValue);
            }
            else {
                throw 'Unknown testDataType:' + testDataType;
            }
            testType = testType.trim().toLowerCase();
            if (testType === 'min') {
                if (valueToCheck < cutoffValue) {
                    this.errorMessages += 'Sorry, the value is too low.';
                    return false;
                }
            }
            else if (testType === 'max') {
                if (valueToCheck > cutoffValue) {
                    this.errorMessages += 'Sorry, the value is too high.';
                    return false;
                }
            }
            else {
                throw 'Unknown test type:' + testType
            }
            return true;
        },
        isValidDate: function(dateString) {
            //https://ctrlq.org/code/20109-javascript-date-valid
            var pieces = dateString.split('/');
            if (pieces.length !== 3) {
                return false;
            }
            var year = parseInt(pieces[0]);
            var month = parseInt(pieces[1]);
            var day = parseInt(pieces[2]);
            var date = new Date();
            date.setFullYear(year, month - 1, day);
            // month - 1 since the month index is 0-based (0 = January)
            return (date.getFullYear() === year)
                && (date.getMonth() === month - 1)
                && (date.getDate() === day);
        }
    },

    /**
     * Save a setting the user entered to the server.
     */
    saveSetting: function () {
        //Validate.
        //Get the machine name of the setting we are trying to save.
        var $widget = $($("#feds-widget"));
        var machineName = $widget.find(".feds-widget-machine-name").val();
        //Get its value. Depends on the type of object it is.
        var valueToCheck = '';
        var widgetType = $widget.find('input[name=' + machineName + ']')
            .attr('type');
        if (widgetType === 'radio') {
            valueToCheck = $widget.find('input[name=' + machineName + ']:checked').val();
        }
        else {
            valueToCheck = $widget.find('input[name=' + machineName + ']').val();
        }
        if (Feds.validators.length > 0) {
            //Init the validator.
            Feds.dataValidator.errorMessages = '';
            Feds.dataValidator.shownGeneralError = false;
            Feds.validators.forEach(function (validator) {
                var testType = validator.testType;
                var testDataType = validator.testDataType;
                var cutoffValue = validator.testValue;
                var errorMessage = validator.errorMessage;
                Feds.dataValidator.check(testType, testDataType,
                    cutoffValue, valueToCheck, errorMessage);
            });
            //Were there validation errors?
            if (Feds.dataValidator.errorMessages !== '') {
                //Yes. Tell user, and abort save.
                alert(Feds.dataValidator.errorMessages);
                return;
            }
        }
        //Validation OK.
        //Send setting to server.
        $.ajax({
            type: 'POST',
            url: Feds.saveSettingUrl,
            data: {
                'projectid': Feds.projectId,
                'machinename': machineName,
                'newValue': valueToCheck
            },
            dataType: 'json'
        }).done(function (data) {
            //XHR success.
            //Check the return data.
            if (data.status === 'ok') {
                //OK
                //Update setting visibility.
                Feds.updateSettingVisibility();
                $.modal.close();
                //Update the display of the setting.
                Feds.updateSettingDisplay(machineName, valueToCheck);
            }
            else {
                console.error(data.status);
            }
        }).fail(function (jqXHR, message) {
            console.error(message);
        });
    },
    updateSettingDisplay: function(machineName, newValue) {
        //Update settings cache.
        Feds.settingsValues[machineName] = newValue;
        //Redo deets display.
        $.ajax({
            type: 'POST',
            url: Feds.settingDisplayUrl,
            data: {
                'projectid': Feds.projectId,
                'machinename': machineName
            },
            dataType: 'json'
        }).done(function (data) {
            //XHR success.
            //Check the return data.
            if ( ! data.deets ) {
                console.error('Bah! No deets');
            }
            if ( data.status !== 'ok'){
                console.log(data.status);
                return;
            }
            //Got the new deets.
            //Replace existing deets.
            $('#' + machineName).closest('.feds-setting-body').html(data.deets);
            //Update setting visibility.
            Feds.updateSettingVisibility();
            //Close the modal.
            $.modal.close();
        }).fail(function (jqXHR, message) {
            console.log(message);
        });
    },
    /*
    Generate a data set.
     */
     generate: function(){
        //Show the status modal.
        var $modal = $($('#generate-modal'));
        Feds.updateGenerateModalState('wait-for-generate');
        $modal.modal();
        //Grab data needed for project description doc generated on the
        //server.
        var settingsState = Feds.getSettingsState();

        //Send a request to the server.
        $.ajax({
            type: 'POST',
            url: Feds.generateUrl,
            data: {
                'projectid': Feds.projectId,
                'settingsstate': JSON.stringify(settingsState),
            },
            dataType: 'json'
        }).done(function (data) {
            //XHR success.
            //Check the return data.
            if ( ! data.archiveurl ) {
                console.error('Bah! No archiveurl');
            }
            if ( data.status !== 'ok' ){
                console.log(data.status);
                return;
            }
            //Got the URL for the archive file.
            $modal.find("#archive-link").attr('href', data.archiveurl);
            Feds.updateGenerateModalState('wait-for-download');
        }).fail(function (jqXHR, message) {
            console.error(message);
        });
    },
    /**
     * Update the display state of the generate data set modal.
     * @param state State to show.
     */
    updateGenerateModalState: function (state) {
        var $modal = $($('#generate-modal'));
        if ( state === 'wait-for-generate') {
            $modal.find("#generate-wait-message").show();
            $modal.find("#delete-wait-message").hide();
            $modal.find("#archive-link-container").hide();
        }
        else if ( state === 'wait-for-download') {
            $modal.find("#generate-wait-message").hide();
            $modal.find("#delete-wait-message").hide();
            $modal.find("#archive-link-container").show();
        }
        else if ( state === 'wait-for-delete') {
            $modal.find("#generate-wait-message").hide();
            $modal.find("#delete-wait-message").show();
            $modal.find("#archive-link-container").hide();
        }
        else {
            console.error('updateGenerateModalState: unknown: ' + state);
        }
    },
    /**
     * Erase the archive for this project.
     */
     eraseArchive: function() {
        Feds.updateGenerateModalState('wait-for-delete');
        //Send a request to the server.
        $.ajax({
            type: 'POST',
            url: Feds.deleteArchiveUrl,
            data: {
                'projectid': Feds.projectId
            },
            dataType: 'json'
        }).done(function (data) {
            if ( data.status !== 'ok'){
                console.log(data.status);
            }
            // OK
            $.modal.close();
        }).fail(function (jqXHR, message) {
            console.error(message);
        });
    },
    /*
    Get the state of visible settings. Values of dependent settings that
    are not visible will not be returned.

    This is used to create the project description that is included in the
    generated data set archive file.
     */
    getSettingsState: function() {
         var result = {};
         $('.feds-setting').each(function(index){
             if ( $(this).css('display') !== 'none') {
                 result[$(this).find('.feds-setting-type').attr('id')]
                    = $(this).find('.feds-value').text();
                 // var setting = {
                 //     'machine_name': $(this).find('.feds-setting-type').attr('id'),
                 //     'value': $(this).find('.feds-value').text()
                 // };
                 // result.push(setting);
             }

         });
         return result;
    },
    showTitleDescriptionWidget: function() {
        $.ajax({
            type: 'POST',
            url: Feds.editTitleDescriptionUrl,
            data: {
                'projectid': Feds.projectId
            },
            dataType: 'json'
        }).done(function (data) {
            //XHR success.
            //Check the return data.
            if ( ! data.widgethtml ) {
                console.error("showTitleDescriptionWidget: Bah! No widget HTML.");
            }
            if ( data.status !== 'ok'){
                console.log(data.status);
                return;
            }
            $('#feds-title-description-widget').html(data.widgethtml);
            $('#title-description-modal-dialog').modal();
        }).fail(function (jqXHR, message) {
            console.error(message);
        });
    },
    /**
     * Save the new project title and description.
     */
    saveTitleDesc: function() {
        //Title can't be MT.
        var $projectTitle = $('#project_title_input');
        var title = $projectTitle.val().trim();
        if ( ! title ) {
            alert('Sorry, title cannot be blank.');
            $projectTitle.focus();
            return false;
        }
        var max_length = $projectTitle.attr('maxlength');
        if ( title.length > max_length ) {
            alert('Sorry, title cannot be more than ' + max_length + ' characters.');
            $projectTitle.focus();
            return false;
        }
        var description  = $('#project_description_input').val().trim();
        //Send data to server.
        $.ajax({
            type: 'POST',
            url: Feds.saveTitleDescriptionUrl,
            data: {
                'projectid': Feds.projectId,
                'title': title,
                'description': description
            },
            dataType: 'json'
        }).done(function (data) {
            //XHR success.
            //Check the return data.
            if (data.status === 'ok') {
                //OK
                //Update display.
                $('#project-title').text(title);
                $('#project-description').text(description);
                $.modal.close();
            }
            else {
                console.error(data.status);
            }
        }).fail(function (jqXHR, message) {
            console.error(message);
        });

    }
};
