# mocovaxfinder
Polls the CVS JSON feed of available appointments to locate open appointments fot COVID vaccine.\
If new appointment slots are available, sends an SMS text message using AWS SNS.\
Designed to be run as an AWS Lambda function.\
Stores the previous set of appointment statuses as a JSON file in the /tmp directory
in the Lambda environment.\



