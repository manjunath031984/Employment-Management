# Employment Management CI -- Jenkins Pipeline Flow

## Pipeline Flow

-   **Declarative: Checkout SCM**
    -   Jenkins loads the `Jenkinsfile` from the configured Git
        repository.
    -   This is the initial SCM checkout performed by Jenkins.
-   **Environment Check**
    -   Displays the pipeline environment and build information.
    -   Verifies the Jenkins build environment before continuing.
-   **Checkout Git Repository**
    -   Checks out the configured GitHub repository.
    -   Uses the configured GitHub credentials.
    -   Builds the selected branch.
-   **Maven Build**
    -   Runs the Maven build for the Employment Management application.
    -   Packages the application and generates the required build
        artifacts.
-   **Maven Test**
    -   Executes the application test cases.
    -   The pipeline continues when the tests complete successfully.
-   **Docker Build**
    -   Builds the Docker image for the Employment Management
        application.
    -   Creates the image using the configured Docker image name and
        version tag.
-   **Docker Hub Input Request**
    -   Pauses the pipeline and requests confirmation from the user.
    -   The user selects whether the Docker image should be pushed to
        Docker Hub.
    -   The pipeline proceeds with the Docker push only when the push
        option is selected.
-   **Docker Hub Login**
    -   Authenticates Jenkins with Docker Hub.
    -   Uses the Docker Hub credentials configured in Jenkins.
-   **Push to Docker Hub**
    -   Pushes the successfully built Docker image to Docker Hub.
    -   The image is pushed to the configured
        `vannalmanju/employment-management` repository.
-   **Pipeline Summary**
    -   Displays the final pipeline execution details.
    -   Shows the build status, branch, environment, image and image
        tag.

## Overall CI Flow

``` text
GitHub Push
    ↓
Declarative: Checkout SCM
    ↓
Environment Check
    ↓
Checkout Git Repository
    ↓
Maven Build
    ↓
Maven Test
    ↓
Docker Build
    ↓
Docker Hub Input Request
    ↓
Docker Hub Login
    ↓
Push to Docker Hub
    ↓
Pipeline Summary
    ↓
Pipeline Completed
```

## Docker Image Flow

``` text
Application Source Code
        ↓
     Maven Build
        ↓
   Maven Test
        ↓
    Docker Build
        ↓
 Docker Image Created
        ↓
   User Approval
        ↓
  Docker Hub Login
        ↓
 Push Image to Docker Hub
```

## Jenkins Pipeline Highlights

-   GitHub is used as the source-code repository.
-   Jenkins automatically executes the CI pipeline when the configured
    trigger is activated.
-   Maven is used to build and test the application.
-   Docker is used to create the application image.
-   Docker Hub is used as the image registry.
-   Jenkins credentials are used for GitHub and Docker Hub
    authentication.
-   An input request provides manual control before pushing the image to
    Docker Hub.
-   The pipeline ends with a summary of the execution.
