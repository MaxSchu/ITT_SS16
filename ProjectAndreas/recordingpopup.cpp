#include "recordingpopup.h"
#include "ui_recordingpopup.h"

RecordingPopup::RecordingPopup(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::RecordingPopup)
{
    ui->setupUi(this);
}

RecordingPopup::~RecordingPopup()
{
    delete ui;
}
