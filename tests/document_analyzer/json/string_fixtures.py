
def minimal_json_string_valid():
    return """
        {
            "firstName": null,
            "lastName": null,
            "jobTitle": null,
            "contactInformation": {
                "emailAddress": null,
                "mobile": null,
                "linkedInAccount": "www.linkedin.com/in/username",
                "twitterAccount": null
            },
            "location": null,
            "dateOfBirth": null,
            "aboutMe": null,
            "hobbies": [],
            "languages": [],
            "education": [],
            "training": [],
            "certificates": [],
            "skills": [],
            "consultancyAssignments": [],
            "books": []
        }
        """

def minimal_json_string_with_trailing_comma_at_end():
    return """
        {
            "firstName": null,
            "lastName": null,
            "jobTitle": null,
            "contactInformation": {
                "emailAddress": null,
                "mobile": null,
                "linkedInAccount": "www.linkedin.com/in/username",
                "twitterAccount": null
            },
            "location": null,
            "dateOfBirth": null,
            "aboutMe": null,
            "hobbies": [],
            "languages": [],
            "education": [],
            "training": [],
            "certificates": [],
            "skills": [],
            "consultancyAssignments": [],
            "books": [],
        }
        """

def minimal_json_string_with_trailing_comma_in_nested_object():
    return """
        {
            "firstName": null,
            "lastName": null,
            "jobTitle": null,
            "contactInformation": {
                "emailAddress": null,
                "mobile": null,
                "linkedInAccount": "www.linkedin.com/in/username",
                "twitterAccount": null
            },
            "location": null,
            "dateOfBirth": null,
            "aboutMe": null,
            "hobbies": [],
            "languages": [],
            "education": [],
            "training": [],
            "certificates": [],
            "skills": [],
            "consultancyAssignments": [],
            "books": []
        }
        """

def minimal_json_string_with_trailing_comma_in_nested_list():
    return """
        {
            "firstName": null,
            "lastName": null,
            "jobTitle": null,
            "contactInformation": {
                "emailAddress": null,
                "mobile": null,
                "linkedInAccount": "www.linkedin.com/in/username",
                "twitterAccount": null
            },
            "location": null,
            "dateOfBirth": null,
            "aboutMe": null,
            "hobbies": [,],
            "languages": [],
            "education": [],
            "training": [],
            "certificates": [],
            "skills": [],
            "consultancyAssignments": [],
            "books": []
        }
        """

def minimal_json_string_with_multiple_trailing_commas():
    return """
        {
            "firstName": null,
            "lastName": null,
            "jobTitle": null,
            "contactInformation": {
                "emailAddress": null,
                "mobile": null,
                "linkedInAccount": "www.linkedin.com/in/username",
                "twitterAccount": null
            },
            "location": null,
            "dateOfBirth": null,
            "aboutMe": null,
            "hobbies": [,],
            "languages": [],
            "education": [],
            "training": [],
            "certificates": [],
            "skills": [],
            "consultancyAssignments": [],
            "books": [],
        }
        """

def minimal_json_string_with_trailing_comma_in_nested_lists():
    return """
        {
            "firstName": null,
            "lastName": null,
            "jobTitle": null,
            "contactInformation": {
                "emailAddress": null,
                "mobile": null,
                "linkedInAccount": "www.linkedin.com/in/username",
                "twitterAccount": null
            },
            "location": null,
            "dateOfBirth": null,
            "aboutMe": null,
            "hobbies": [,],
            "languages": [,],
            "education": [],
            "training": [],
            "certificates": [],
            "skills": [],
            "consultancyAssignments": [],
            "books": []
        }
        """

def empty_json_object():
    return """
        {
        }
        """

def json_string_with_object_at_end_with_trailing_comma():
    return """
        {
            "firstName": null,
            "lastName": null,
            "jobTitle": null,
            "contactInformation": {
                "emailAddress": null,
                "mobile": null,
                "linkedInAccount": "www.linkedin.com/in/username",
                "twitterAccount": null
            },
        }
        """

def json_string_with_object_at_end_valid():
    return """
        {
            "firstName": null,
            "lastName": null,
            "jobTitle": null,
            "contactInformation": {
                "emailAddress": null,
                "mobile": null,
                "linkedInAccount": "www.linkedin.com/in/username",
                "twitterAccount": null
            }
        }
        """

def json_string_with_string_at_end_with_trailing_comma():
    return """
        {
            "firstName": null,
            "lastName": null,
            "jobTitle": "title",
        }
        """

def json_string_with_string_at_end_valid():
    return """
        {
            "firstName": null,
            "lastName": null,
            "jobTitle": "title"
        }
        """

def json_string_with_no_whitspace_with_trailing_comma():
    return """{"firstName": null,"lastName": null,"jobTitle": null,"contactInformation":{"emailAddress": null,"mobile": null,"linkedInAccount": "www.linkedin.com/in/username","twitterAccount": null,},"location": null,"dateOfBirth": null,"aboutMe": null,"hobbies": ["climbing",],"languages": [],"education": [],"training": [],"certificates": [],"skills": [],"consultancyAssignments": [],"books": [],}"""

def json_string_with_no_whitespace_valid():
    return """{"firstName": null,"lastName": null,"jobTitle": null,"contactInformation":{"emailAddress": null,"mobile": null,"linkedInAccount": "www.linkedin.com/in/username","twitterAccount": null},"location": null,"dateOfBirth": null,"aboutMe": null,"hobbies": ["climbing"],"languages": [],"education": [],"training": [],"certificates": [],"skills": [],"consultancyAssignments": [],"books": []}"""
