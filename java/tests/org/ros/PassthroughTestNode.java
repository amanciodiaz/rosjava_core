/*
 * Copyright (C) 2011 Google Inc.
 * 
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy of
 * the License at
 * 
 * http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations under
 * the License.
 */
package org.ros;

import org.ros.exceptions.RosInitException;
import org.ros.exceptions.RosNameException;

/**
 * This node is used in rostest end-to-end integration tests with other client
 * libraries.
 * 
 * @author kwc@willowgarage.com (Ken Conley)
 */
public class PassthroughTestNode implements RosMain {

  @Override
  public void rosMain(String[] argv, NodeContext nodeContext) throws RosNameException,
      RosInitException {
    final Node node;
    node = new Node("test_node", nodeContext);
    node.init();

    // The goal of the passthrough node is simply to retransmit the messages
    // sent to it. This allows us to external verify that the node is compatible
    // with multiple publishers, multiple subscribers, etc...

    // String pass through
    final Publisher<org.ros.message.std_msgs.String> pub_string = node.createPublisher("string_out",
        org.ros.message.std_msgs.String.class);
    MessageListener<org.ros.message.std_msgs.String> string_cb = new MessageListener<org.ros.message.std_msgs.String>() {
      @Override
      public void onNewMessage(org.ros.message.std_msgs.String m) {
        pub_string.publish(m);
      }
    };
    node.createSubscriber("string_in", string_cb, org.ros.message.std_msgs.String.class);
    
    //Int64 pass through
    final Publisher<org.ros.message.std_msgs.Int64> pub_int64 = node.createPublisher("int64_out",
        org.ros.message.std_msgs.Int64.class);
    MessageListener<org.ros.message.std_msgs.Int64> int64_cb = new MessageListener<org.ros.message.std_msgs.Int64>() {
      @Override
      public void onNewMessage(org.ros.message.std_msgs.Int64 m) {
        pub_int64.publish(m);
      }
    };
    node.createSubscriber("int64_in", int64_cb, org.ros.message.std_msgs.Int64.class);
    
    //TestHeader pass through
    final Publisher<org.ros.message.test_ros.TestHeader> pub_header = node.createPublisher("test_header_out",
        org.ros.message.test_ros.TestHeader.class);
    MessageListener<org.ros.message.test_ros.TestHeader> header_cb = new MessageListener<org.ros.message.test_ros.TestHeader>() {
      @Override
      public void onNewMessage(org.ros.message.test_ros.TestHeader m) {
        m.orig_caller_id = m.caller_id;
        m.caller_id = node.getName();
        pub_header.publish(m);
      }
    };
    node.createSubscriber("test_header_in", header_cb, org.ros.message.test_ros.TestHeader.class);

    //TestComposite pass through
    final Publisher<org.ros.message.test_ros.Composite> pub_composite = node.createPublisher("composite_out",
        org.ros.message.test_ros.Composite.class);
    MessageListener<org.ros.message.test_ros.Composite> composite_cb = new MessageListener<org.ros.message.test_ros.Composite>() {
      @Override
      public void onNewMessage(org.ros.message.test_ros.Composite m) {
        pub_composite.publish(m);
      }
    };
    node.createSubscriber("composite_in", composite_cb, org.ros.message.test_ros.Composite.class);
    
    // just spin until exit
    while (true) {
      try {
        Thread.sleep(100);
      } catch (InterruptedException e) {
        e.printStackTrace();
      }
    }

  }
}