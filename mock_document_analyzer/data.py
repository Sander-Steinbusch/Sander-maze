def get_test_data():
    return {
        "firstName": "John", 
        "lastName": "Doe", 
        "jobTitle": "Software Engineer", 
        "contactInformation": {
            "emailAddress": "johndoe@email.com", 
            "mobile": "+1 123-456-7890", 
            "linkedInAccount": "https://www.linkedin.com/in/johndoe/", 
            "twitterAccount": "https://twitter.com/johndoe", 
        }, 
        "location": "San Francisco", 
        "dateOfBirth": "1990-01-01", 
        "aboutMe": "I am a software engineer with 5 years of experience in developing web applications using Java and JavaScript.", 
        "hobbies": [
            "Reading", 
            "Hiking"
        ], 
        "languages": [
            {
                "name": "English", 
                "score": 5
            }, 
            {
                "name": "Spanish", 
                "score": 3
            }
        ], 
        "education": [
            {
                "name": "Computer Science", 
                "institute": {
                    "name": "University of California, Berkeley"
                }, 
                "startYear": 2010, 
                "endYear": 2014
            }
        ], 
        "training": [
            {
                "name": "React Native", 
                "institute": { 
                    "name": "Udemy"
                }, 
                "year": 2018
            }
        ], 
        "certificates": [
            {
                "name": "Oracle Certified Java Developer", 
                "institute": {
                    "name": "Oracle"
                }, 
                "year": 2015
            }
        ], 
        "skills": [
            {
                "name": "Java", 
                "score": 5
            },
            {
                "name": "JavaScript", 
                "score": 4
            },
            {
                "name": "React", 
                "score": 3
            }
        ], 
        "consultancyAssignments": [
            {
                "project": {
                    "name": "Software Engineer", 
                    "customer": {
                        "name": "Google"
                    }
                },
                "startedOn": "2015-01-01", 
                "stoppedOn": "2017-12-31", 
                "description": "Developed web applications using Java and JavaScript.", 
                "roles": [
                    "Developer", 
                    "Team Lead"
                ], 
                "skills": [
                    "Java", 
                    "JavaScript", 
                    "Agile Methodology"
                ]
            }, 
            {
                "project": {
                    "name": "Software Engineer", 
                    "customer": {
                        "name": "Facebook"
                    }
                },
                "startedOn": "2018-01-01", 
                "stoppedOn": None, 
                "description": "Developing web applications using React and Node.js.", 
                "roles": [
                    "Developer"
                ], 
                "skills": [
                    "React", 
                    "Node.js", 
                    "GraphQL"
                ]
            }
        ], 
        "books": [
            {
                "title": "Clean Code", 
                "author": "Robert C. Martin", 
                "publishingYear": 2008
            }
        ]
    }