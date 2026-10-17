
## Assessment feature implementation

This educational fork adds Question, Choice and Submission models, inline admin editing,
an enrolled-user exam form, POST-only submission and owner-only result pages. Multiple-choice
grading requires the exact correct set; selecting an additional incorrect choice earns no points.
The provided template's pass threshold remains greater than 80 percent.

Run `python manage.py migrate`, then `python manage.py test onlinecourse.test_assessment`.
The eight tests use Django's in-process client, including successful and failed exams,
partial and extra selections, enrollment checks and cross-user result isolation.
No public production deployment is claimed. The starter's dependencies and development
settings are for the course lab. Codex assisted with implementation and verification.

**General Notes**

An `onlinecourse` app has already been provided in this repo upon which you will be adding a new assesement feature.

- If you want to develop the final project on Theia hosted by [IBM Developer Skills Network](https://labs.cognitiveclass.ai/), you will need to create the same project structure on Theia workspace and save it everytime you close the browser
- Or you could develop the final project locally by setting up your own Python runtime and IDE
- Hints for the final project are left on source code files
- You may choose any cloud platform for deployment (default is IBM Cloud Foundry)
- Depends on your deployment, you may choose any SQL database Django supported such as SQLite3, PostgreSQL, and MySQL (default is SQLite3)

**ER Diagram**
For your reference, we have prepared the ER diagram design for the new assesement feature.

![Onlinecourse ER Diagram](https://github.com/ibm-developer-skills-network/final-cloud-app-with-database/blob/master/static/media/course_images/onlinecourse_app_er.png)
