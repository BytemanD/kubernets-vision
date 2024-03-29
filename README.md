# kubernetes-vision

Kubernetes Dasboard With Vuetify

预览

![](./doc/preview.png)

## 启动容器
```
VERSION=latest
mkdir -p /etc/kubevision
cp ~/.kube/config /etc/kubevision

cat <<EOF > /etc/kubevision/kubevision.conf
[k8s]
kube_config = /etc/kubevision/config
EOF

podman run -itd --network=host --name kubevision -v /etc/kubevision:/etc/kubevision kubevision:${VERSION}
```

*更多用法参考帮助信息。*

## 常用命令
```bash
kubectl create sa kubevision
kubectl create token kubevision
kubectl create clusterrolebinding
kubectl create clusterrolebinding kubevision-admin --clusterrole=cluster-admin --user=kubevision

kubectl create rolebinding kubevision-rolebinding --clusterrole=admin --serviceaccount=kubevision

```
Token
```
eyJhbGciOiJSUzI1NiIsImtpZCI6IjdCalJFNkRYelhpOGpULVl1dmVqM1phV3NBZzl1OW5zclVySWRhaGpLakkifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjLmNsdXN0ZXIubG9jYWwiXSwiZXhwIjoxNjc2Mzg2ODQ5LCJpYXQiOjE2NzYzODMyNDksImlzcyI6Imh0dHBzOi8va3ViZXJuZXRlcy5kZWZhdWx0LnN2Yy5jbHVzdGVyLmxvY2FsIiwia3ViZXJuZXRlcy5pbyI6eyJuYW1lc3BhY2UiOiJkZWZhdWx0Iiwic2VydmljZWFjY291bnQiOnsibmFtZSI6Imt1YmV2aXNpb24iLCJ1aWQiOiJlNDM0ZmNiMS03NWRjLTQ5MjMtYTU0Yi0xMGMwNjgwZmRkOTAifX0sIm5iZiI6MTY3NjM4MzI0OSwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50OmRlZmF1bHQ6a3ViZXZpc2lvbiJ9.Kh0_ICLBe2zSz67I2-n7kXiC-HYLuSaMk0lwsVcdoqyD51U2kwNy-fMM7t2NuErQDfeh2Zpv5B7KNHX2nSToTpHMiZ-LBE2ahSIB_ExOCJEQHPZoYM4QFcbY-OZ8reQNSZ6lx-Q5TYb03o3tTkk0BflxHWaPAl2OJWIW6j_43ANtrR7dUqkauFVgZjC5QGKujNDRi_BprWPbk2VzkKSs_1jGljNu0eln3OpUyoYrUay_X3YR1-guYblbHecXRh6AWnUUNMDJV4DH41DzWqoA1h4eaNNViADol9cz8Tb1uHuXlXCbbuF9hpe7mO5WiE9p1ZsvHuKkckozUo1maVKAvw
```

## ChangeLog

[ChangeLog](./doc/ChangeLog.md)
