# get rid of old stuff
docker rmi -f $(docker images | grep "^<none>" | awk "{print $3}")
docker rm $(docker ps -q -f status=exited)

docker kill drugshot
docker rm drugshot

docker build -f Dockerfile -t maayanlab/drugshot:1.1 .

docker push maayanlab/drugshot:1.1
