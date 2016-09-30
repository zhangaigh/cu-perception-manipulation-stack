#ifndef PERCEPTION_PARAM_H
#define PERCEPTION_PARAM_H

#include <ros/ros.h>
#include <string>

namespace perception
{
  enum task_running { TASK0 = 0, TASK1 = 1} task;

  //cup with spoon
  double cws_height_min;
  double cws_height_max;
  double cws_xy_min;
  double cws_xy_max;
  int cws_objects = 0;

  //spoon without cup split
  double spoon_start_height;

  //plate
  double plate_height_min;
  double plate_height_max;
  double plate_xy_min;
  double plate_xy_max;
  int plate_objects = 0;

  //bowl
  double bowl_height_min;
  double bowl_height_max;
  double bowl_xy_min;
  double bowl_xy_max;
  int bowl_objects = 0;

  //published labels
  const std::string cws_label = "cup_with_spoon";
  const std::string cup_label = "cup";
  const std::string spoon_label = "spoon";
  const std::string bowl_label = "bowl";
  const std::string plate_label = "plate";
  const std::string hammer_label = "hammer";
  const std::string unknown_label = "unknown";
  int unknown_objects = 0;

  std::vector<std::string> object_labels;

}


#endif // PERCEPTION_PARAM_H
