## Running locally (e.g. for testing)

```
pip install -r ./requirements.txt
python3 ./lambda_function.py
```

(Note that this simply runs the lambda event handler once - therefore the
caching isn't really tested)

## Current testing endpoint

Currently available to test at https://8yt84sq5d4.execute-api.af-south-1.amazonaws.com/default/loadshedding

The expected output is something like:
```
{
  "status": {
    "eskom_status": {
      "stage": 0,
      "time": "2021-11-14T19:38:34.537481"
    },
    "cot_status": {
      "stage": 0,
      "time": "2021-11-14T19:38:35.307747"
    }
  }
}
```

The stage is only updated at a maximum of once every minute.

## updating the deployed code

Based on instructions found in https://docs.aws.amazon.com/lambda/latest/dg/python-package.html

1. Run ./1_create_lambda_zip.sh
2. Upload deployment-package.zip to your AWS Lambda


