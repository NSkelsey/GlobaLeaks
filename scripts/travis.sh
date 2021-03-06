#!/bin/bash

set -e

if [ "$GLTEST" = "unit" ]; then
  echo "Running Mocha testes for API"
  cd $TRAVIS_BUILD_DIR/backend
  coverage run setup.py test
  coveralls || true
  $TRAVIS_BUILD_DIR/backend/bin/globaleaks -z travis
  sleep 5
  $TRAVIS_BUILD_DIR/client/node_modules/mocha/bin/mocha -R list $TRAVIS_BUILD_DIR/client/tests/api/test_00* --timeout 30000

elif [ "$GLTEST" = "browserchecks" ]; then

  echo "Running Mocha tests for browser compatibility"
  grunt test-browserchecks-saucelabs

else

  echo "Running Protractor End2End tests"

  declare -a capabilities=(
    "export SELENIUM_BROWSER_CAPABILITIES='{\"browserName\":\"firefox\", \"version\":\"37.0\", \"platform\":\"Windows 10\"}'"
    "export SELENIUM_BROWSER_CAPABILITIES='{\"browserName\":\"chrome\", \"version\":\"42.0\", \"platform\":\"Windows 10\"}'"
    "export SELENIUM_BROWSER_CAPABILITIES='{\"browserName\":\"safari\", \"version\":\"8\", \"platform\":\"OS X 10.10\"}'"
    "export SELENIUM_BROWSER_CAPABILITIES='{\"browserName\":\"internet explorer\", \"version\":\"11\", \"platform\":\"Windows 10\"}'"
    "export SELENIUM_BROWSER_CAPABILITIES='{\"browserName\":\"microsoftedge\", \"version\":\"20.10240\", \"platform\":\"Windows 10\"}'"
    "export SELENIUM_BROWSER_CAPABILITIES='{\"browserName\":\"android\", \"version\": \"5.1\", \"deviceName\": \"Android Emulator\", \"platform\": \"Linux\", \"platform\":\"OS X 10.10\"}'"
    "export SELENIUM_BROWSER_CAPABILITIES='{\"browserName\": \"iphone\", \"version\": \"8.2\", \"deviceName\": \"iPhone Simulator\", \"device-orientation\": \"portrait\", \"platform\":\"OS X 10.10\" }'"
  )

  ## now loop through the above array
  for i in "${capabilities[@]}"
  do
    echo "Testing Configuration: $i"
    eval $i
    $TRAVIS_BUILD_DIR/backend/bin/globaleaks -z travis -c -k9 --port 9000
    sleep 3
    grunt protractor:saucelabs
  done

fi
