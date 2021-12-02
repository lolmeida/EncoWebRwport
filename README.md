gcloud builds submit --tag gcr.io/testbed-779346371066/encostreamlitreport --project=testbed-779346371066

cloud run deploy --image qcr.io/testbed-779346371066/encostreamlitreport --platform managed --project=testbed-779346371066-allow-unauthenticated