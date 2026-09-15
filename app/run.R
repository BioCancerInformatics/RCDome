# RCDome Atlas — launcher para o serviço systemd.
# O serviço executa:  Rscript /mnt/sharefiles/servicos/RCDome_Atlas/APP/run.R
# com WorkingDirectory no diretório do app, então "." resolve para a pasta do app.
shiny::runApp(
  appDir         = ".",
  host           = "0.0.0.0",
  port           = 8890,
  launch.browser = FALSE
)
