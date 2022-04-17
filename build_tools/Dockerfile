FROM odoo:13.0
LABEL maintainer="Oakland  Tech <m.abdalla@odooerp.ae>"


USER root

COPY ./build_tools/image-scripts/entrypoint.sh /
RUN chmod +x /entrypoint.sh

RUN pip3 install redis

COPY build_tools/addons_ci /mnt/addons_ci
COPY build_tools/image-configs/dev.conf /etc/odoo/odoo.conf
COPY build_tools/image-configs/stage.conf /etc/odoo/
COPY build_tools/image-configs/prod.conf /etc/odoo/
RUN chown odoo /etc/odoo/odoo.conf


COPY ./addons /mnt/addons
COPY ./addons_dependencies /mnt/addons_dependencies
COPY ./addons_extra /mnt/addons_extra

#USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
