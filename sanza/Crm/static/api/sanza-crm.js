angular.module('services').service(
  'backend',
  [
    '$http', 'config', '$q', '$log', function ($http, config, $q, $log) {
      // AngularJS will instantiate a singleton by calling "new" on this function

      var _getApi = function(url) {
        return $q(function(resolve, reject) {
          var fullUrl = config.backendPrefix + url;
          $http.get(fullUrl).success(function (data) {
            resolve(data);
          }).error(function() {
            reject();
          });
        });
      };

      var _putApi = function(url, putData) {
        return $q(function(resolve, reject) {
          var fullUrl = config.backendPrefix + url;
          $http.put(fullUrl, putData).success(function (data) {
            resolve(data);
          }).error(function() {
            reject();
          });
        });
      };

      var _postApi = function(url, putData) {
        return $q(function(resolve, reject) {
          var fullUrl = config.backendPrefix + url;
          $http.post(fullUrl, putData).success(function (data) {
            resolve(data);
          }).error(function() {
            reject();
          });
        });
      };

      var _deleteApi = function(url, putData) {
        return $q(function(resolve, reject) {
          var fullUrl = config.backendPrefix + url;
          $http.delete(fullUrl, putData).success(function (data) {
            resolve(data);
          }).error(function() {
            reject();
          });
        });
      };

      var updateEventDate = function(eventId, data) {
        return _putApi('/crm/api/update-action-date/'+eventId+'/', data);
      };

      var updateEvent = function(eventId, data) {
        return _putApi('/crm/api/update-action/'+eventId+'/', data);
      };

      var createEvent = function(data) {
        return _postApi('/crm/api/create-action/', data);
      };

      var deleteEvent = function(eventId, data) {
       return _deleteApi('/crm/api/delete-action/'+eventId+'/', data);
      };

      var getContactsList = function(name) {
        return _getApi('/crm/api/contacts/?name='+name);
      };

      var getContact = function(id) {
        return _getApi('/crm/api/contacts/'+id);
      };

      return {
        updateEventDate: updateEventDate,
        updateEvent: updateEvent,
        createEvent: createEvent,
        deleteEvent: deleteEvent,
        getContactsList: getContactsList,
        getContact: getContact
      };
    }
  ]
);
