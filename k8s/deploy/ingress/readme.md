# Ingress Deployment Scripts

This directory contains scripts and manifests to deploy and configure NGINX Ingress and cert-manager for Kubernetes clusters.

## Structure

- `main.sh`  
  Main script to install, upgrade, and uninstall NGINX Ingress and cert-manager, and apply related manifests.
- `nginx-controller/`  
  - `manifest/airflow-ingress.yaml`: Example Ingress resource for Airflow.
  - `helm/`: Helm values for NGINX Ingress.
- `cert-manager/`  
  - `manifest/clusterissuer-letsencrypt.yaml`: ClusterIssuer for Let's Encrypt.
  - `helm/`: Helm values for cert-manager.

## Usage

1. **Run the main script**  
   This will install NGINX Ingress and cert-manager, apply required manifests, and set up TLS with Let's Encrypt.

   ```sh
   ./main.sh
   ```

2. **Check certificate status**
    After applying, check the status of your certificate:

    ```
    kubectl get certificate -n <namespace>
    ```

3. **Uninstall**
    The script also contains commands to uninstall all resources.

## Notes
 - Ensure your DNS points to the Ingress controller's external IP before running the script.
 - Port 80 (HTTP) must be open and accessible for Let's Encrypt HTTP-01 challenge.
 - The script assumes you have kubectl and helm installed and configured.


<br><br><br><br><br>


# All steps to set up Ingress, Ingress controller and cert manager

Steps to Configure Airflow Webserver Ingress on GCP

## 1. Reserve a Premium Static IP in GCP
- Navigate to the **VPC Network** > **External IP addresses** in the GCP Console.
- Reserve a new static IP address: ```34.134.107.91```

## 2. Register and Configure a Domain in GCP
- Register a domain using **Google Domains** : ```airflow.default-data.com```
- Configure the domain's DNS settings (Cloud DNS) to point to the static IP address reserved in the previous step.

## 3. Exposing the Airflow Webserver via HTTPS on GKE with NGINX Ingress and Let’s Encrypt
This section is automated in the `main.sh` script.

### a) Install the NGINX Ingress controller with the static IP

```yaml
controller:
    service:
        type: LoadBalancer
        loadBalancerIP: 34.134.107.91 # premium static IP in GCP
        loadBalancerSourceRanges: 
        - 34.170.248.193/32 # ip address do twingate
```
```shell
helm upgrade --install ingress-controller ingress-nginx/ingress-nginx \
    --version 4.12.1 \
    -f ingress/nginx-controller/manifest/helm/values-nginx-2-0-1.yaml \
    --namespace nginx
```
This deploys the NGINX Ingress controller and creates a Service of type LoadBalancer using the reserved premium static IP. Wait a minute or two for the external IP to be assigned.

> **Important:**  
> For the Let's Encrypt HTTP-01 challenge to succeed, you must initially set `loadBalancerSourceRanges` to `0.0.0.0/0` to allow public HTTP access:
>
> ```yaml
> loadBalancerSourceRanges:
>   - 0.0.0.0/0
> ```
>
> After the TLS certificate is successfully issued and validated, update `loadBalancerSourceRanges` to restrict access to only your Twingate IP address for security:
>
> ```yaml
> loadBalancerSourceRanges:
>   - 34.170.248.193/32 # Twingate IP address
> ```
>
> Let’s Encrypt must be able to reach your Kubernetes Ingress controller on HTTP (port 80) to validate the domain. Even if you intend to serve your application only on HTTPS, port 80 must remain open during certificate issuance.


### b) Install cert-manager (Certificate Controller)

```shell
helm upgrade --install cert-manager cert-manager/cert-manager \
    --version 1.17.1 \
    -f ingress/cert-manager/manifest/helm/values-cert-manager-1-17-1.yaml \
    --namespace cert-manager
```

### c) Configure a ClusterIssuer for Let’s Encrypt
Now set up Let’s Encrypt as a certificate issuer cluster-wide, so it can provide TLS certificates for our Ingress.

In this ClusterIssuer, we specify Let’s Encrypt’s production ACME server URL, an email for registration, and enable the HTTP-01 challenge solver using our NGINX ingress controller (class: nginx). 

The *privateKeySecretRef* is the Kubernetes Secret where the ACME account key will be stored (it will be created automatically).
```shell
kubectl apply -f ingress/cert-manager/manifest/clusterissuer-letsencrypt.yaml -n cert-manager
```

### d) Create an Ingress for the Airflow Webserver Service

> **Note:** This step is critical and may require troubleshooting. Carefully review each configuration.

Define an Ingress resource to route external HTTPS traffic to the `airflow-webserver` service and use cert-manager to automatically obtain a TLS certificate from Let's Encrypt.

The HTTP-01 challenge is triggered when you apply the following command, provided that:

- The annotation `cert-manager.io/cluster-issuer: "letsencrypt-prod"` is present.
- The `tls` section requests a certificate for your domain.
- The `host` matches your DNS and points to your GKE Ingress IP.

At this point, cert-manager will:

- Create a Certificate resource.
- Set up a temporary Challenge and helper Ingress.
- Wait for Let’s Encrypt to call `http://yourdomain.com/.well-known/acme-challenge/<token>`.

Apply the Ingress manifest:

```shell
kubectl apply -f ingress/nginx-controller/manifest/airflow-ingress.yaml -n airflow
```

This configuration will:

- Route HTTPS traffic for `airflow.default-data.com` to the `airflow-webserver` service on port 8080.
- Request a TLS certificate from Let's Encrypt using the `letsencrypt-prod` ClusterIssuer.
- Store the certificate in the `airflow-webserver-tls` secret.
- Redirect all HTTP traffic to HTTPS.

The `tls` section defines the host and the name of the TLS secret (`airflow-webserver-tls`). Cert-manager will create this secret and store the obtained certificate.

Within a minute or so, cert-manager will detect the new Ingress and create a Certificate request for the specified host. It will complete the ACME HTTP-01 challenge automatically by provisioning a temporary challenge Ingress. You can check the status of the certificate with:

```sh
kubectl get certificate airflow-webserver-tls -n airflow
```

Once the certificate status is `READY`, update the NGINX Ingress controller to restrict access to your Twingate IP address for improved security:

```yaml
loadBalancerSourceRanges:
    - 34.170.248.193/32 # Twingate IP address
```

Finally, navigate to `https://airflow.default-data.com` in your browser. You should see the Airflow web UI served via the NGINX Ingress, secured with a Let’s Encrypt TLS certificate. All HTTP requests will be automatically redirected to HTTPS.


## 4. Troubleshooting

If you encounter issues with certificate issuance or Ingress access, follow these steps:

1. **Verify DNS Resolution**
    ```sh
    nslookup airflow.default-data.com
    ```
    Ensure your domain resolves to the correct static IP.

2. **Check Ingress Controller Accessibility on Port 80**
    ```sh
    curl -v http://airflow.default-data.com/.well-known/acme-challenge/test
    ```
    Confirm that HTTP requests reach the Ingress controller.

3. **Inspect Ingress and Certificate Resources**
    ```sh
    kubectl get ingress -A | grep airflow
    kubectl get certificate -A
    kubectl get challenge -A
    ```
    Check that the Ingress, Certificate, and Challenge resources exist and are in the expected state.

4. **Reapply the Ingress Manifest and Retry Certificate Issuance**
    ```sh
    kubectl apply -f ingress/nginx-controller/manifest/airflow-ingress.yaml -n airflow
    kubectl delete certificate airflow-webserver-tls -n airflow
    ```
    Deleting a failed Certificate resource allows cert-manager to retry the issuance process.

If problems persist, review cert-manager and ingress controller logs for more details.

