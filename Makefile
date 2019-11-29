TAG?=v4
REGISTRY?=m00nf1sh/reinvent2019con310r

docker-build:
	docker build -t $(REGISTRY):$(TAG) .

docker-push: docker-build
	docker push $(REGISTRY):$(TAG)

deploy: docker-push
	cat deploy/deploy.yaml | sed "s;image: .*;image: $(REGISTRY):$(TAG);" | kubectl apply -f -

master:
	kubectl set env deployment/reinvent2019con310r MESSAGE="The master"

monitor:
	watch -n 1 kubectl get pods

attack:
	echo "GET http://$(shell kubectl get ingress/reinvent2019con310r -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')"	| \
    vegeta attack -rate 100 -duration 1m | vegeta encode | tee result.bin | \
    jaggr @count=rps \
          hist\[100,200,300,400,500\]:code \
          p25,p50,p95:latency | \
    jplot code.hist.100+code.hist.200+code.hist.300+code.hist.400+code.hist.500 \
	&& cat result.bin | vegeta report