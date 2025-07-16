DATE=$(date)
echo "Fixing 502 at ${DATE}"

sudo mkdir -p /var/run/uwsgi
sudo chown www-data:www-data /var/run/uwsgi
sudo systemctl restart uwsgi.service
sudo systemctl restart nginx.service

echo "Finished"
echo ""