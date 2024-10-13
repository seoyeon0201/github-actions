**GitHub Actions 정상동작 확인 후 AWS 리소스 모두 지웠으므로 현재는 실행 X! 코드 업로드하지 말 것**

## GitHub Actions & AWS CodeDeploy

1. Local에서 코드 작성 후 GitHub에 Push
2. GitHub에서 자체 VM 생성 후 S3에 파일 업로드
3. S3에 Code Deploy에 S3 파일을 가져와 EC2에 저장하라는 명령어 발송
4. EC2는 Code Deploy 명령어를 받아 S3로부터 정보 가져옴

## 진행사항

1. S3 bucket, folder 생성
2. 권한 설정
- EC2에서 S3와 Code Deploy에 배포하기 위한 권한 (Role)
- Code Deploy에서 EC2에 S3 데이터를 저장하기 위한 권한 (Role)
- GitHub에서 S3에 저장하고 Code Deploy하기 위한 권한 (Users)
- GitHub에서 EC2에 push하기 위한 액세스 키 생성 (csv)
  - aws access key와 secret key GitHub Secrets로 설정

3. EC2 생성
4. CodeDeploy Application 생성
5. EC2에 CodeDeploy 설치
6. 로컬에 appspec.yml 파일 추가
7. GitHub Actions Workflow 생성


## 결과

- AWS S3 folder에 GitHub에 업로드한 코드를 모은 하나의 tar.gz 파일 업로드 
- AWS CodeDeploy Deployments Success
- EC2 내에 GitHub에 업로드한 코드 모두 존재


## GitHub Actions Workflow

```
name: Python Application with AWS CodeDeploy

on:
  push:
    branches: [ main ]

permissions:
  contents: read

env:
  S3_BUCKET_NAME: githuactions-codedeploy-bucket
  AWS_REGION: ap-northeast-2

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
    # 1. 저장소 체크아웃
    - uses: actions/checkout@v4

    # 2. Python 3.12 설치
    - name: Set up Python 3.12
      uses: actions/setup-python@v4
      with:
        python-version: "3.12"

    # 3. Python 의존성 설치
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flake8 pytest
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

    # 4. Linting 수행 (flake8)
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

    # 5. 애플리케이션 실행 (테스트)
    - name: Run the application
      run: python app.py

    # 6. 아카이브 파일 생성
    - name: Archive Application
      run: tar cvfz ./awsbeginner.tar.gz *
    
    - name: Check AWS Secret Key
      run: |
        echo "${{ secrets.AWS_ACCESS_KEY }}" | wc -c
        echo "${{ secrets.AWS_SECRET_KEY }}" | wc -c
        
    # 7. AWS 자격 증명 구성
    - name: AWS configure credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_KEY }}
        aws-region: ap-northeast-2

    
    # 8. S3에 파일 업로드
    - name: Upload to S3
      run: aws s3 cp --region ap-northeast-2 ./awsbeginner.tar.gz s3://githuactions-codedeploy-bucket/githubactions-codedeploy-folder/
    
    # 9. AWS CodeDeploy로 배포
    - name: Deploy with AWS CodeDeploy
      run: aws deploy create-deployment --application-name githubactions-codedeploy --deployment-config-name CodeDeployDefault.AllAtOnce --deployment-group-name githubactions-codedeploy-group --s3-location "bucket=githuactions-codedeploy-bucket,bundleType=tgz,key=githubactions-codedeploy-folder/awsbeginner.tar.gz"
```
