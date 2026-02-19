- install python 3.12 sudo dnf install -y python3.12

login into aws clodshell
git clone my-git repo https://github.com/contactdhawan/lex-helper.git
create a folder lex-lambda-layer ast same level as lex-helper
cd lex-helper-layer
python3.12 -m pip install /home/cloudshell-user/lex-helper -t python/lib/python3.12/site-packages/ --upgrade


clean https://github.com/aws/lex-helper/blob/main/docs/LAMBDA_LAYER_DEPLOYMENT.md#step-3-clean-up-unnecessary-files
```
# Remove Python cache files
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete

# Remove test files and directories
find . -type d -name "tests" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +

# Remove development files
find . -name "*.egg-info" -exec rm -rf {} +
find . -name ".git*" -delete
find . -name "*.md" -delete
find . -name "LICENSE*" -delete
```

zip -r ../lex-helper-layer.zip .

zip https://github.com/aws/lex-helper/blob/main/docs/LAMBDA_LAYER_DEPLOYMENT.md#create-zip-archive

cd ..

aws lambda publish-layer-version \
    --layer-name lex-helper-layer \
    --description "Lex Helper Library - Version $(date +'%Y-%m-%d')" \
    --zip-file fileb://lex-helper-layer.zip \
    --compatible-runtimes python3.12 \
    --compatible-architectures x86_64 arm64
