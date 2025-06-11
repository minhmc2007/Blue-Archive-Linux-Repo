import QtQuick 2.5

Rectangle {
    id: root
    color: "#2a3950"
    
    property int stage
    
    onStageChanged: {
        if (stage == 1) {
            introAnimation.running = true
        }
    }
    
    Item {
        id: content
        anchors.fill: parent
        opacity: 0
        
        Rectangle {
            anchors.centerIn: parent
            width: 300
            height: 200
            color: "transparent"
            
            Text {
                anchors.centerIn: parent
                text: "BlueArchive-Shiroko"
                color: "#4381d0"
                font.pixelSize: 24
                font.bold: true
            }
        }
        
        OpacityAnimator {
            id: introAnimation
            running: false
            target: content
            from: 0
            to: 1
            duration: 1000
            easing.type: Easing.InOutQuad
        }
    }
}
