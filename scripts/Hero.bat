for /f "delims=" %%i in ('heroku config:get DATABASE_URL -a your-app-name') do setx DATABASE_URL %%i
echo %DATABASE_URL%
pause