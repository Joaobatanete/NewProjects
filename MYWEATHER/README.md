My CS50 final Project consists of a Weather forecastweb-based application, using Python, Flask, SQL, HTML5, CSS3 and JavaScript.

With a login and registration element, it allows the user to search for the current City Weather data, displaying its: country; temperature; description; humidity; wind; and date. 
Saving every search, in the index page, where it can compare with other current City's Weather. 

Keeping track in the History page for all the different City's searched so it can later be compared, to check the difference of the data value.
Also a delete button is available to each City searched, so it can manage the index page as the user likes. 

Displaying a flash message every time an action takes place, or an error occurs.

The main code can be found in application.py, where it contains the login, register, index, logout, history, and delete routes.

The Weather Data extraction function from the API, and transformation using json, with the current date time function, and the login required, are inserted in weather.py.

For the database, it's stored in weather.db, within three different data tables:
- users: for usernames and passwords storage;
- weather_data: for each user can check its weather data storage;
- history: for each user can check its weather data recorded;

For templates, using HTML, CSS and JavaScript, with Bulma and Bootstrap documentation:
- layout.html;
- login.html;
- register.html;
- index.html;
- history.html;

And styles.css for static.

Thank you, hope you like it!

João Batanete