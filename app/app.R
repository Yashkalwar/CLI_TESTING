library(shiny)

people <- data.frame(
  Name = c("Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace", "Heidi"),
  Age  = c(30, 45, 28, 39, 52, 33, 41, 26),
  Dept = c("Sales", "Engineering", "HR", "Engineering", "Sales", "HR", "Engineering", "Sales"),
  stringsAsFactors = FALSE
)

ui <- fluidPage(
  titlePanel("Dummy People App"),
  sidebarLayout(
    sidebarPanel(
      textInput("user_name", "Name"),
      numericInput("age", "Age", value = NA, min = 1, max = 120),
      selectInput("dept", "Department", choices = c("All", "Sales", "Engineering", "HR")),
      actionButton("submit", "Submit")
    ),
    mainPanel(
      textOutput("error_msg"),
      textOutput("greeting"),
      tableOutput("people_table")
    )
  )
)

server <- function(input, output, session) {
  rv <- reactiveValues(error = "", greeting = "")

  observeEvent(input$submit, {
    name <- trimws(input$user_name)
    if (is.null(input$user_name) || !nzchar(name)) {
      rv$error <- "Name is required"
      rv$greeting <- ""
    } else if (is.na(input$age) || input$age < 1 || input$age > 120) {
      rv$error <- "Age must be between 1 and 120"
      rv$greeting <- ""
    } else {
      rv$error <- ""
      rv$greeting <- paste0("Hello, ", name, "! You are ", input$age, " years old.")
    }
  })

  output$error_msg <- renderText(rv$error)
  output$greeting <- renderText(rv$greeting)

  output$people_table <- renderTable({
    df <- if (input$dept == "All") people else people[people$Dept == input$dept, ]
    if (nrow(df) == 0) data.frame(Message = "No results") else df
  })
}

shinyApp(ui, server)
