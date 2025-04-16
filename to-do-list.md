End goal: user installs WSL + Ubuntu, then runs setup.sh to provision a full dev environment — no manual Python, MongoDB, or Docker setup needed.

May want to include in setup script something to set uLimits for MongoDB (this may also affect elasticsearch)

I'm going to need to make an updatable to check environment variable to set client depending on whether it'ss test or prod (Was I sleep deprived when I wrote this sentence?)

Need to figure out how to automatically swtich based on ENV variable (production vs testing) 

curiosity: benefits of JSON vs YAML?


Upon return: Mimic ES logic from chemicals in lots.



Add to docs: future upgrades:
THESE GO ON THE README ITSELF TO SHOW I THINK ABOUT SYSTEM DESIGN
Add ability to search specific list of lots to future upgrades (not one lot, not all lots, but a specific subset, such as all lots returned by an ES query)
Implement internal lot numbers for lots to have more human-readable identifiers for lots
ES could then be used as follows:
* User needs to find available bottles of a chemical
* search returns result cards with indexed information: just enough to identify ltos (name, human-readable internal lot number, prepared/opened date, expiry date, empty date). When they click the result they want, MongoDB is then queried to return the rest of the information on the page that loads.

Notes for documentation:
ES only stores chemical names and ids
ES stores lot names, Mongo_ids, prepared/opened dates, expiry dates, and empty dates.
It does this to keep documents and maintenance as lightweight as possible.
Search chemicals or lots by name, find the one you need with it's id, then
query it in mongodb for all information
* Move ES record construction into class methods like document construction


Will need to load some more data: Duplicate lots in various quantities to show off ability to pull aggregate data and find the most popular classifications/chemicals
ES endpoints:
* Return aggregate values based on fuzzy search for chemical name?
* Return aggregate values based on fuzzy search for lot name?
*
* Find most popular chemical based on fuzzy search by name?
* (Double-check the prompt at this point now that the hard part is over)




# Where to pick up:
* Add ElasticSearch integration
* Update README, specifications.md, and api_reference.md to include ElasticSearch integration
* Finish README
* Proofread README.md, specification.md, and api_reference.md
    * api_reference.md needs error code returns standardized. Use testing strategy section for this.
    * Project file trees in both need final update
* Perform a clean reinstall of WSL and the project to ensure it works like the README says it does for set-up.