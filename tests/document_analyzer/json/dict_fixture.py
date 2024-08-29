
def dict_with_empty_book():
    return {
        "firstName": None,
        "lastName": None,
        "jobTitle": "Team Coach | Scrum Master | QA Tester",
        "contactInformation": {
            "emailAddress": None,
            "mobile": None,
            "linkedInAccount": None,
            "twitterAccount": None
        },
        "location": "Hechtel-Eksel, Flemish Region, Belgium",
        "dateOfBirth": None,
        "aboutMe": None,
        "hobbies": [],
        "languages": [],
        "education": [],
        "training": [],
        "certificates": [],
        "skills": [],
        "consultancyAssignments": [],
        "books": [
            {
                "title": None,
                "author": None,
                "publishingYear": None
            }
        ]
    }

def dict_valid():
    return {
        "firstName": None,
        "lastName": None,
        "jobTitle": "Team Coach | Scrum Master | QA Tester",
        "contactInformation": {
            "emailAddress": None,
            "mobile": None,
            "linkedInAccount": None,
            "twitterAccount": None
        },
        "location": "Hechtel-Eksel, Flemish Region, Belgium",
        "dateOfBirth": None,
        "aboutMe": None,
        "hobbies": [],
        "languages": [],
        "education": [],
        "training": [],
        "certificates": [],
        "skills": [],
        "consultancyAssignments": [],
        "books": []
    }

def dict_with_empty_language():
    return {
        "firstName": None,
        "lastName": None,
        "jobTitle": "Team Coach | Scrum Master | QA Tester",
        "contactInformation": {
            "emailAddress": None,
            "mobile": None,
            "linkedInAccount": None,
            "twitterAccount": None
        },
        "location": "Hechtel-Eksel, Flemish Region, Belgium",
        "dateOfBirth": None,
        "aboutMe": None,
        "hobbies": [],
        "languages": [
            {
                "name": None,
                "score": None
            }
        ],
        "education": [],
        "training": [],
        "certificates": [],
        "skills": [],
        "consultancyAssignments": [],
        "books": []
    }

def dict_with_empty_consultancy_assignment():
    return {
        "firstName": None,
        "lastName": None,
        "jobTitle": "Team Coach | Scrum Master | QA Tester",
        "contactInformation": {
            "emailAddress": None,
            "mobile": None,
            "linkedInAccount": None,
            "twitterAccount": None
        },
        "location": "Hechtel-Eksel, Flemish Region, Belgium",
        "dateOfBirth": None,
        "aboutMe": None,
        "hobbies": [],
        "languages": [],
        "education": [],
        "training": [],
        "certificates": [],
        "skills": [],
        "consultancyAssignments": [
            {
                "project": {
                    "name": None,
                    "customer": {
                        "name": None
                    }
                },
                "startedOn": None,
                "stoppedOn": None,
                "description": None,
                "roles": [],
                "skills": []
            }
        ],
        "books": []
    }

def dict_with_hobbies():
    return {
        "firstName": None,
        "lastName": None,
        "jobTitle": "Team Coach | Scrum Master | QA Tester",
        "contactInformation": {
            "emailAddress": None,
            "mobile": None,
            "linkedInAccount": None,
            "twitterAccount": None
        },
        "location": "Hechtel-Eksel, Flemish Region, Belgium",
        "dateOfBirth": None,
        "aboutMe": None,
        "hobbies": [
            "Climbing",
            "Gaming",
            ""
        ],
        "languages": [],
        "education": [],
        "training": [],
        "certificates": [],
        "skills": [],
        "consultancyAssignments": [],
        "books": []
    }

def list_with_empty_dict():
    return [
        {
            "title": None,
            "author": None,
            "publishingYear": None
        }
    ]

def list_with_both_empty_and_valid_dict():
    return [
        {
            "title": None,
            "author": None,
            "publishingYear": None
        },
        {
            "title": "title",
            "author": None,
            "publishingYear": None
        },
        {
            "title": None,
            "author": None,
            "publishingYear": None
        },
        {
            "title": None,
            "author": None,
            "publishingYear": 2015
        }
    ]

def list_with_only_valid_dict():
    return [
        {
            "title": "title",
            "author": None,
            "publishingYear": None
        },
        {
            "title": None,
            "author": None,
            "publishingYear": 2015
        }
    ] 

def list_with_strings():
    return [
        "title",
        "author",
        "publishingYear"
    ]