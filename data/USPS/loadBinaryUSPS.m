% function to load digits from the usps set for a binary class task. The
% arguments specify which digits are used. The targets are +/- 1.0. The cases
% are ordered according to class. Returns x and y for training and xx and yy
% for testing.
%
% Copyright (C) 2005 and 2006, Carl Edward Rasmussen, 2006-03-13.

function [x, y, xx, yy] = loadBinaryUSPS(D1, D2, D3);

try
  load usps_resampled.mat
catch
  disp('Error: the file usps_resampled.mat was not found. Perhaps you need to')
  disp('download the file from http://www.gaussianprocess.org/gpml/data ?')
  x = []; y = []; xx = []; yy = [];
  return
end

IND1 = train_labels(D1+1,:) == 1;           % offset by 1 as we label from zero
IND2 = train_labels(D2+1,:) == 1;
IND3 = train_labels(D3+1,:) == 1;
x = [train_patterns(:,IND1)'; train_patterns(:,IND2)';train_patterns(:,IND3)'];
y = [zeros(sum(IND1),1); zeros(sum(IND2),1)+1; zeros(sum(IND3),1)+2];

ITE1 = test_labels(D1+1,:) == 1;            % offset by 1 as we label from zero
ITE2 = test_labels(D2+1,:) == 1;
ITE3 = test_labels(D3+1,:) == 1;
xx = [test_patterns(:,ITE1)'; test_patterns(:,ITE2)'; test_patterns(:,ITE3)'];
yy = [zeros(sum(ITE1),1); zeros(sum(ITE2),1)+1; zeros(sum(ITE3),1)+2];

csvwrite('train.csv',[y,x])
csvwrite('test.csv',[yy,xx])