# Authentication Model

## Storage

### Api User Model

#### Items

##### UUID

##### Secret Token

###### The real token is never revealed into the database, only the SHA512 hash is stored there.

######  The real hash is used as a encryption key for the Session Key and creds

###### Real hash's value is known only to the user

##### Kirkes Credentials and Session Key

###### Values are encrypted using the secret token

##### Session Key creation date and last used date

###### Values are encrypted using the secret token

## Authentication process

### Logging in

#### When logging in, Backend will create a new object, and random token. Random token is for authentication

##### More details about storing data can be found on the "Storage" section

### Validating token and using kirkes

#### Validating token

##### Validating token is just comparing hashes in database, if hashed value of user's token matches any hashes in db

###### If any matches found, authentication is complete

###### If no matches found, authentication fails

#### Using kirkes

##### Using the token, Backend will decrypt Session Key, and if it's invalid, it will renew it by decrypting username and password

###### Then when Session key is validated (checking the last used date, or relogging in), API will make a request to the server
