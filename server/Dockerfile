FROM odoo:13.0
LABEL maintainer="Oakland  Tech <m.abdalla@odooerp.ae>"


USER root

COPY image-scripts/entrypoint.sh /
RUN chmod +x /entrypoint.sh

RUN pip3 install redis

#COPY build_tools/addons_ci /mnt/addons_ci
COPY image-configs/dev.conf /etc/odoo/odoo.conf
RUN chown odoo /etc/odoo/odoo.conf


COPY ./custom_addons /mnt/custom_addons
COPY ./addons_dependencies /mnt/addons_dependencies
#COPY ./addons_extra /mnt/addons_extra

#USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
