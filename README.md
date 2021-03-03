# openfinna API server
OpenFinna Server is a project aimed to offer open APIs to Kirkes and Finna for everyone who wants it (that includes libraries in Tuusula, Järvenpää, Kerava, Mäntsälä and 20+ more). For that this backend is providing "proxy", which makes it easy to use Finna's basic functionality as a REST API

## To-Do list
- [x] Backend Login
- [x] API Login
- [x] Get holds
- [x] Get loans
- [x] Renew loans
- [x] Change hold's pickup location
- [x] Get pickup locations
- [x] Search
- [x] Resource details
- [x] Reserve something (i.e. a book)
- [x] Change default pickup location
- [x] Get default pickup location (also in Get Pickup Locations request)
- [x] Get fines
- [ ] Get fines payment link
- [x] Get user information
- [ ] Edit user information
- [ ] Get library cards list
- [ ] Support multiple library cards
- [ ] API Call for attaching a new card to user's account
- [ ] Change PIN-code


## Why is this existing in the first place?
No library provider nor finna itself give any API to their library system. Finally, here comes the solution to this problem.
tem.

## How does it work?
By parsing HTML, and some JSON (AJAX calls)
#### Authentication:
![Authentication Diagram](https://raw.githubusercontent.com/openfinna/server/master/authentication_model.png)
