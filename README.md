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
- [ ] Change default pickup location
- [ ] Get fees
- [ ] Get fee's payment link
- [ ] Edit user information
- [ ] Get library cards list
- [ ] Support multiple library cards
- [ ] API Call for attaching a new card to user's account


## Why is this existing in the first place?
Because almost every library (when requesting APIs) looks at you and say "We don't give you any APIs, we aren't interested in you, go and do whatever you want, please don't contact us again, yOU aRe a sEcUrItY tHrEat!", but when a company enters the stage and requests the API, they go, hug them, and hand it over. That's why, because of unprofessional people, who works only for the money. None of us can do anything about this. Only solution to make this API that doesn't rely on the Library System.

## How does it work?
By parsing HTML, and some JSON (AJAX calls)
