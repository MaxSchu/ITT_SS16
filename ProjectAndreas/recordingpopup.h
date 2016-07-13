#ifndef RECORDINGPOPUP_H
#define RECORDINGPOPUP_H

#include <QMainWindow>

namespace Ui {
class RecordingPopup;
}

class RecordingPopup : public QMainWindow
{
    Q_OBJECT

public:
    explicit RecordingPopup(QWidget *parent = 0);
    ~RecordingPopup();

private:
    Ui::RecordingPopup *ui;
};

#endif // RECORDINGPOPUP_H
