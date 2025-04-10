"""
The aggregate fields "Available_Total" and "Available_Open" in the chemicals schema depend on the presence of lot records.
As such, their testing neither quite fits neatly into the chemicals/ nor the lots/ test groups.

# Chemical Total_Available and Total_Open field behaviour:
* Chemical aggregate fields are initialized to int(0) upon chemical template creation.
* Chemical aggregate fields will change as a result of lots being open, emptied, or their expiry date passing.
* Chemical aggregate fields are recalculated when a PUT or GET request is submitted for a chemical(s).
* Chemical aggregate fields are recalculated for a chemical template when lots are created or updated.
* Chemical aggregate fields are NOT recalculated when lots are deleted. Though the system currently supports lot deletion,
it is marked for an upgrade to remove the ability to delete lots (or anything, for that matter). A very high-level
user may need access to truly delete records, but the system should isntead have "Removed" field flags for all objects,
and "deleting" an object should merely set the "Removed" flaag to "True".
    * This would be considered a critical issue if this system were live.
        * (It's not live; it's a portfolio piece that I'm burned out on after 11 days of LITERAL dawn-to-dusk effort.)
* Chemical aggregate fields are technically updates when a chemical template receives a PUT request, but this is obfuscated by the
fact that chemical aggregate fields are updated when a GET request is received for the template.



# To-Do:
* Update chemical GET requests to update the parent chemical aggregate fields.
* Update lot PUT and POST requests to update the parent chemical templates aggregate fields.



# Test design:
* Post all cehmical templates and store objects and primary keys.
* Check aggregate data on chemical templates. Total/Open should be 0/0 for purchased lots and 1/1 for prepared lots.
* Run post_all_lots() and store objects and primary keys.
* Check aggregate data on chemical templates again. Total/Open should be 2/0 for purchased lots and 2/2 for prepared lots.
* Update purchased lots to give them an open date.
* Check aggregate data on chemical templates again. Total/Open should be 2/2 for purchased lots and 2/2 for prepared lots.
* Update all lots to have an empty date.
* Check aggregate data on chemical templates again. Total/Open should be 0/0 for purchased lots and 0/0 for prepared lots.
* Update all lots to have no empty date.
* Check aggregate data on chemical templates again. Total/Open should be 2/2 for purchased lots and 2/2 for prepared lots.
* Update all lots to have a passed expiry date.
* Check aggregate data on chemical templates again. Total/Open should be 0/0 for purchased lots and 0/0 for prepared lots.
* If possible, set all lots to have expiry dates 15 seconds from now and update them.
* Check aggregate data on chemical templates again. Total/Open should be 2/2 for purchased lots and 2/2 for prepared lots.
* After waiting for 15 seconds, check aggregate data on chemical templates again. Total/Open should be 0/0 for purchased lots and 0/0 for prepared lots.
"""