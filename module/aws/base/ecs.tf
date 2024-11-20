# module "cluster" {
#   source = "git::https://github.sys.cigna.com/cigna/ECS-Golden-Module.git//submodules/ecs-cluster-fargate?ref=2.5.1"
#
#   product_name = var.project_name
#   #subsidiary_prefix = "usm"
#
#   required_tags      = var.required_common_tags
#   required_data_tags = var.required_data_tags
# }
#
# module "rolling_update_alb_coco" {
#   source = "git::https://github.sys.cigna.com/cigna/ECS-Golden-Module.git//submodules/alb-nlb-golden-vpc?ref=2.5.1"
#
#   name                      = var.project_name
#   vpc_id                    = local.vpc_id
#   use_evernorth_hosted_zone = false
#   nlb_route_53_subdomain    = var.frontend_route53_record_name
#   alb_ssl_policy            = "ELBSecurityPolicy-TLS13-1-2-2021-06"
#   alb_subnets               = local.private_subnet_ids
#   #subsidiary_prefix         = "usm"
#
#   alb_healthcheck_block = {
#     path     = "/admin"
#     port     = 443
#     protocol = "HTTPS"
#     matcher  = "200-399"
#   }
#
#   required_tags      = var.required_common_tags
#   required_data_tags = var.required_data_tags
# }
#
# module "service_rolling_update" {
#   source = "git::https://github.sys.cigna.com/cigna/ECS-Golden-Module.git//submodules/ecs-service-task?ref=2.5.1"
#
#   name           = "${var.project_name}-ru"
#   cluster_name   = module.cluster.ecs_cluster_name
#   vpc_id         = local.vpc_id # module.golden-vpc.vpc.id
#   container_name = "${var.project_name}-nginx"
#   container_port = 443
#   desired_count  = var.django_service_config.desired
#   min_capacity   = var.django_service_config.min_capacity
#   max_capacity   = var.django_service_config.max_capacity
#
#   task_role_arn = aws_iam_role.container_iam_role.arn
#
#   enable_service_api_ingress = true
#   alb_security_group_id      = module.rolling_update_alb_coco.cluster_alb_security_group_id
#
#   container_cpu         = 4096
#   container_memory      = 8192
#   container_definitions = jsonencode([module.nginx_container_definition.json_map_object, module.python_container_definition.json_map_object])
#
#   health_check_grace_period_seconds = 180
#   healthcheck_block = {
#     path                = "/admin"
#     protocol            = "HTTPS"
#     healthy_threshold   = 2
#     unhealthy_threshold = 2
#     matcher             = "301"
#     interval            = 30
#     timeout             = 20
#   }
#
#   tags = var.required_common_tags
#
#   depends_on = [module.rolling_update_alb_coco]
# }
#
# resource "aws_lb_listener_rule" "host_based_weighted_routing" {
#   listener_arn = module.rolling_update_alb_coco.cluster_alb_listener_arn
#   priority     = 100
#
#   action {
#     type             = "forward"
#     target_group_arn = module.service_rolling_update.service_target_group_arn
#   }
#
#   condition {
#     host_header {
#       values = ["${var.frontend_route53_record_name}.${local.route_53_private_zone_name}"]
#     }
#   }
# }
#
# module "nginx_container_definition" {
#   source  = "cloudposse/ecs-container-definition/aws"
#   version = "0.58.1"
#
#   container_cpu                = 1024
#   container_memory_reservation = 2048
#   container_image              = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${data.aws_region.current.name}.amazonaws.com/${var.project_name}-nginx:1.0"
#   container_name               = "${var.project_name}-nginx"
#
#   log_configuration = {
#     logDriver = "awslogs"
#     options = {
#       "awslogs-create-group"  = true
#       "awslogs-group"         = aws_cloudwatch_log_group.cluster_service_logs.name
#       "awslogs-region"        = data.aws_region.current.name
#       "awslogs-stream-prefix" = "${var.project_name}-nginx/service-task-logs"
#     }
#   }
#
#   port_mappings = [
#     {
#       containerPort = 443
#       hostPort      = 443
#       protocol      = "tcp"
#     }
#   ]
# }
#
# module "python_container_definition" {
#   source  = "cloudposse/ecs-container-definition/aws"
#   version = "0.58.1"
#
#   container_cpu                = 1024
#   container_memory_reservation = 2048
#   container_image              = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${data.aws_region.current.name}.amazonaws.com/${var.project_name}-python:${var.django_container_tag}"
#   container_name               = "${var.project_name}-python"
#
#   log_configuration = {
#     logDriver = "awslogs"
#     options = {
#       "awslogs-create-group"  = true
#       "awslogs-group"         = aws_cloudwatch_log_group.cluster_service_logs.name
#       "awslogs-region"        = data.aws_region.current.name
#       "awslogs-stream-prefix" = "${var.project_name}-python/service-task-logs"
#     }
#   }
#
#   map_environment = {
#     CLOUDFRONT_DNS   = aws_route53_record.cloudfront_record.fqdn
#     STATIC_S3_BUCKET = split(":::", module.static_assets_bucket.s3_bucket_arn)[1]
#     FRONTEND_HOST    = "*" # "${var.frontend_route53_record_name}.${local.route_53_private_zone_name}"
#     DB_USER          = var.db_username
#     RDS_ENDPOINT     = module.aurora_serverless_coco.rds_proxy_endpoint
#     DB_SECRET_NAME   = aws_secretsmanager_secret.db_creds_secret.name
#     ENABLE_DEBUG     = var.log_level == "DEBUG" && var.environment != "prod" ? "true" : "false"
#   }
#
#   map_secrets = {
#     DJANGO_SECRET_STRING = aws_secretsmanager_secret.django_secret_string.id
#     AIRFLOW_SECRET       = aws_secretsmanager_secret.td_creds_secret.id
#     #DB_SECRET            = aws_secretsmanager_secret.db_creds_secret.id
#   }
#
#   port_mappings = [
#     {
#       containerPort = 8000
#       hostPort      = 8000
#       protocol      = "tcp"
#     }
#   ]
# }
#
# module "migration_container_definition" {
#   source  = "cloudposse/ecs-container-definition/aws"
#   version = "0.58.1"
#
#   container_cpu                = 256
#   container_memory_reservation = 512
#   container_image              = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${data.aws_region.current.name}.amazonaws.com/${var.project_name}-python:${var.django_container_tag}"
#   container_name               = "${var.project_name}-migration"
#
#   command = ["sh", "-c", "python3 manage.py collectstatic --noinput && python3 manage.py makemigrations && python3 manage.py migrate"]
#   log_configuration = {
#     logDriver = "awslogs"
#     options = {
#       "awslogs-create-group"  = true
#       "awslogs-group"         = aws_cloudwatch_log_group.cluster_service_logs.name
#       "awslogs-region"        = data.aws_region.current.name
#       "awslogs-stream-prefix" = "${var.project_name}-migration/service-task-logs"
#     }
#   }
#
#   map_environment = {
#     CLOUDFRONT_DNS   = aws_route53_record.cloudfront_record.fqdn
#     STATIC_S3_BUCKET = split(":::", module.static_assets_bucket.s3_bucket_arn)[1]
#     FRONTEND_HOST    = "*"
#     DB_USER          = var.db_username
#     RDS_ENDPOINT     = module.aurora_serverless_coco.rds_proxy_endpoint # module.aurora_serverless.endpoint
#     DB_SECRET_NAME   = aws_secretsmanager_secret.db_creds_secret.name
#     ENABLE_DEBUG     = var.log_level == "DEBUG" && var.environment != "prod" ? "true" : "false"
#   }
#
#   map_secrets = {
#     DJANGO_SECRET_STRING = aws_secretsmanager_secret_version.django_secret_string_version.secret_id
#     AIRFLOW_SECRET       = aws_secretsmanager_secret.td_creds_secret.id
#     #DB_SECRET            = aws_secretsmanager_secret.db_creds_secret.id
#   }
# }
#
# resource "aws_ecs_task_definition" "migration_task" {
#   family                   = "${var.project_name}-migration"
#   requires_compatibilities = ["FARGATE"]
#   network_mode             = "awsvpc"
#   cpu                      = 256
#   memory                   = 512
#   container_definitions    = module.migration_container_definition.json_map_encoded_list
#
#   task_role_arn      = aws_iam_role.container_iam_role.arn
#   execution_role_arn = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${module.service_rolling_update.task_execution_role_name}"
# }
#
# module "superuser_container_definition" {
#   source  = "cloudposse/ecs-container-definition/aws"
#   version = "0.58.1"
#
#   container_cpu                = 256
#   container_memory_reservation = 512
#   container_image              = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${data.aws_region.current.name}.amazonaws.com/${var.project_name}-python:${var.django_container_tag}"
#   container_name               = "${var.project_name}-superuser"
#
#   command = ["sh", "-c", "python3 manage.py createsuperuser --noinput "]
#   log_configuration = {
#     logDriver = "awslogs"
#     options = {
#       "awslogs-create-group"  = true
#       "awslogs-group"         = aws_cloudwatch_log_group.cluster_service_logs.name
#       "awslogs-region"        = data.aws_region.current.name
#       "awslogs-stream-prefix" = "${var.project_name}-superuser/service-task-logs"
#     }
#   }
#
#   # https://docs.djangoproject.com/en/3.0/ref/django-admin/#django-admin-createsuperuser
#   map_environment = {
#     CLOUDFRONT_DNS            = aws_route53_record.cloudfront_record.fqdn
#     STATIC_S3_BUCKET          = split(":::", module.static_assets_bucket.s3_bucket_arn)[1]
#     FRONTEND_HOST             = "*"
#     DB_USER                   = var.db_username
#     RDS_ENDPOINT              = module.aurora_serverless_coco.rds_proxy_endpoint # module.aurora_serverless.endpoint
#     DB_SECRET_NAME            = aws_secretsmanager_secret.db_creds_secret.name
#     DJANGO_SUPERUSER_USERNAME = var.superuser_username
#     DJANGO_SUPERUSER_EMAIL    = "admin@cigna.com"
#     DJANGO_SETTINGS_MODULE    = "ccsera_django.settings"
#     ENABLE_DEBUG              = var.log_level == "DEBUG" && var.environment != "prod" ? "true" : "false"
#   }
#
#   map_secrets = {
#     DJANGO_SECRET_STRING      = aws_secretsmanager_secret_version.django_secret_string_version.secret_id
#     AIRFLOW_SECRET            = aws_secretsmanager_secret.td_creds_secret.id
#     DJANGO_SUPERUSER_PASSWORD = aws_secretsmanager_secret_version.superuser_creds_secret_version.secret_id
#   }
# }
#
# resource "aws_ecs_task_definition" "superuser_create_task" {
#   family                   = "${var.project_name}-superuser-creation"
#   requires_compatibilities = ["FARGATE"]
#   network_mode             = "awsvpc"
#   cpu                      = 256
#   memory                   = 512
#   container_definitions    = module.superuser_container_definition.json_map_encoded_list
#
#   task_role_arn      = aws_iam_role.container_iam_role.arn
#   execution_role_arn = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${module.service_rolling_update.task_execution_role_name}"
# }
#
# resource "aws_security_group_rule" "https_egress" {
#   type              = "egress"
#   from_port         = 443
#   to_port           = 443
#   protocol          = "tcp"
#   cidr_blocks       = ["0.0.0.0/0"]
#   security_group_id = module.service_rolling_update.service_security_group_id
# }
#
# resource "aws_security_group_rule" "allow_ecs_proxy_egress" {
#   type                     = "egress"
#   from_port                = 5432
#   to_port                  = 5432
#   protocol                 = "tcp"
#   source_security_group_id = aws_security_group.rds_proxy_sg.id
#   security_group_id        = module.service_rolling_update.service_security_group_id
# }
#
# resource "aws_security_group_rule" "allow_ecs_proxy_ingress" {
#   type                     = "ingress"
#   from_port                = 5432
#   to_port                  = 5432
#   protocol                 = "tcp"
#   source_security_group_id = module.service_rolling_update.service_security_group_id
#   security_group_id        = aws_security_group.rds_proxy_sg.id
# }
#
# resource "aws_security_group_rule" "https_ingress" {
#   type              = "ingress"
#   from_port         = 443
#   to_port           = 443
#   protocol          = "tcp"
#   cidr_blocks       = ["10.0.0.0/8"]
#   security_group_id = module.rolling_update_alb_coco.cluster_alb_security_group_id
# }
#
# resource "aws_cloudwatch_log_group" "cluster_service_logs" {
#   name              = "${var.project_name}-ecs-log-group"
#   retention_in_days = 0
#   tags              = var.required_common_tags
# }
