# open kirkes
OpenKirkes is a project aimed to offer open APIs to Kirkes for everyone who wants it (that includes libraries in Tuusula, Järvenpää, Kerava and Mäntsälä). For that this backend is providing "proxy", which makes it easy to use Kirkes' basic functionality as a REST API

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


## Why is this existing in the first place?
All libraries refused to give me API access, I was very disappointed, I even tried to be nice to them, waited two months to get an answer. I was empty handed at that point, and started thinking about other ways. Only solution was to make this API that doesn't rely on their Library System.

## How does it work?
By parsing HTML, and some JSON (AJAX calls)
#### Authentication:
![Authentication Diagram](https://raw.githubusercontent.com/developerfromjokela/open-kirkes/master/authentication_model.png)
