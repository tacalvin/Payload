#ifndef _NETWORK_WIDGET_H
#define _NETWORK_WIDGET_H

#include "StarPacket0x01.h"
#include "Network.h"
#include <QPushButton>
#include <QDockWidget>
#include <QLineEdit>
#include <QString>
#include <QLabel>
#include <QObject>
#include <iostream>

class NetworkWidget : public QDockWidget{
	Q_OBJECT
	public:
		explicit NetworkWidget(QWidget *parent=0);
	private:
		QString ipAddress;
		QLineEdit *ipInput;
		QLineEdit *portInput;
		QLineEdit *networkStatus;
		QLabel *networkLabel;		
		QLabel *ipLabel;
		QLabel *portLabel;
		QPushButton *networkButton;		
		QPushButton *connectButton;
		QPushButton *disconnectButton;
		Network *net;
		StarPacket0x01 testPacket; //for testing purposes.

	signals:

	public slots:
		//Connect function
		void setConnect();
		//Disconnect function
		void setDisconnect();
		//Check Network Status function
		void checkNetwork();
};

#endif
