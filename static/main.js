(function () {

  'use strict';

  angular.module('WordcountApp', [])

  .controller('WordcountController', ['$scope', '$log', '$http', '$timeout',
    function($scope, $log, $http, $timeout) {

    $scope.getResults = function() {

      $log.log("test");

      // get the URL from the input
      var userInput = $scope.url;

      // fire the API request
      $http.post('/start', {"url": userInput}).
        then(function(results) {
          $log.log(results);
          getWordCount(results.data);

        }).
        catch(function(error) {
          $log.log(error);
        });

    };

    function getWordCount(jobID) {

      var timeout = "";

      var poller = function() {
        // fire another request
        $http.get('/results/'+jobID).
          then(function(data, status, headers, config) {
            if(status === 202) {
              $log.log(data, status);
            } else if (status === 200){
              $log.log("data");
              $log.log(data);
              $scope.wordcounts = data;
              $timeout.cancel(timeout);
              return false;
            }
            // continue to call the poller() function every 2 seconds
            // until the timeout is cancelled
            timeout = $timeout(poller, 1000);
          });
      };
      poller();
    }

  }
  ]);

}());
