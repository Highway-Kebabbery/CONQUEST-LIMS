README: Use | jq to get formatted responses
Tell users to run the cleaning script and re-start the app on the off chance it fails.
It's rare, but I have had one or two failures in the smoke test stage that aren't repeatable.
note in specs, readme, or both that es lot doc design stores minimal info: enough for something like a card on the front end to display enough information to be recognizable to an analyst such that they could click the card and then load a page that queries the full record from MongoDB
# Where to pick up:
* Finish README
* Proofread README.md, api_reference.md
    * api_reference.md needs error code returns standardized. Use testing strategy section for this.
* Perform a clean reinstall of WSL and the project to ensure it works like the README says it does for set-up.