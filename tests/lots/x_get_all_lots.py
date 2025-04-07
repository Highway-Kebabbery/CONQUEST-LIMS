# Initial notes:
'''
* DON'T FORGET TO TEST AGGREGATE FIELDS



I need to build:
* updated valid chemical purchased 1
* Updated valid chemical purchased 2
* Updated valid prepared chemical 1

I need to:
* POST valid purchased chemical 1
* POST valid purchased chemical 2
* POST valid prepared chemical 1
* Save all three _ids

* Note that system does not currently reject requests to update (replace) a chemical with 
a request for a prepared chemical that uses the replaced chemical in one of its components
(This operation would remove the reference required for the new chemical, but it would pass
the initial checks because it's an edge case).
* Update valid purchased chemical 1 with updated valid purchased chemical 1
* Update valid purchased chemical 2 with updated valid purchased chemical 2
* Update valid prepared chemical 1 with updated valid prepared chemical 1
* This tests all valid, like-for-like updates

DELETE all three _ids, re-POST the chemicals, and re-save the new _ids to reset the
test environment.

* Update purchased chem 1 with alt prepared chem 1
* Update purchased chem 2 with alt prepared chem 1
* Update prepared chem 1 with alt purchased chem 1
* This tests that updates with non-similar but valid requests will work and also
avoids reference issues related to adding a purchased chemical by removing the chemical
template implicitly referenced by one of its components.
    * Come back to add test for this later after implementing that validation.

Testing 422 error code:
* Try to update valid purch chem 1 with all invalid permutations in invalid_chemicals
* Try to update valid purch chem 2 with all invalid permutations in invalid_chemicals
* Try to update valid prep chem 1 with all invalid permutations in invalid_chemicals
* This tests 422 in all cases when attempting to update a valid chem with an invalid
chem: prepared chems with prepared chems, purchased chems with purchased chems,
prepared chems with purchased chems, and purchased chems with prepared chems.
'''
