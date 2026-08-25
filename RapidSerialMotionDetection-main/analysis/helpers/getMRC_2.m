function [RMC_2_mat] = getMRC_2(SEQUENCE)
% -------------------------------------------------------------------------
% MOTION REVERSE CORRELATION (SECOND ORDER)
% -------------------------------------------------------------------------
% This function performs the second order Motion Reverse Correlation (MRC). 
% It computes the (normalized) propabilities for each (1st) impuses with 
% certain motion direction and at certain time latency to precede another 
% (2nd) impulse preceding the response onset. Probabilities time courses 
% (across all latencies) for each directions of the impulses are low-passed
% at 4 Hz to reduce noise. Probabilities are returned as table for further 
% analysis of correlogram and tuning curves.
%
%
% INPUT
%       SEQUENCE : table
%           Paramters of each impulse within the sequence of each trial
%             - Onset           : time stamp of each impulse onset
%             - Direction       : motion direction of each impulse
%             - Validity        : logical index if impulses were valid
%             - Response_Onset  : time stamp of each response onset
%
% OUTPUT
%       RMC_2_mat : table
%           Correlation values of an impulse at ceratin diretion and at
%           certain latencz to precede a response onset
%             - Latnecy     : time lage of impulse to response onset (ms)
%             - Direction   : Each impulse direction (-90 to 255 deg)
% -------------------------------------------------------------------------



% ----- SETTINGS ----------------------------------------------------------

latency_min = -1225;
latency_max = 375;

lag_bins    = (latency_min:50:latency_max);     % latency bin
dir_bins    = (-90 : 15 : 255);      	        % directions bin

nLag = numel(lag_bins);


% map each bin to one group (direction triplet)
nGroups     = numel(dir_bins)/3;        % number of direction groups
dir_group   = repelem(1:nGroups, 3);
dir_group   = circshift(dir_group, -1); % shift one step back



% ----- COUNT IMPULSES ACROSS TRIALS --------------------------------------

% preallocate
COUNT_ARRAY = zeros(nLag, nGroups, nGroups);   % 3-D array
COUNT_MAT    = nan(numel(lag_bins)-1, nGroups^2);           % 2-D matrix


% iteration over trials
for tr = 1:size(SEQUENCE, 1)

    % get paramters of corresponding trial
    IMP_ONSET       = SEQUENCE.Onset{tr};
    IMP_DIR         = SEQUENCE.Direction{tr};
    IMP_VALID       = SEQUENCE.Validity{tr};
    RESPONSE_ONSET  = SEQUENCE.Response_Onset{tr};



    % ----- DEFINE TIME WINDOW OF INVALID RESPONSES -----------------------
        
    % last valid impulse preceding invalid impusles
    last_valid_before_invalid = find(IMP_VALID(1:end-1) & ...
                                     ~IMP_VALID(2:end));

    % preallocate
    exclude_windows = zeros(numel(last_valid_before_invalid), 2);


    % get time stamps
    for i = 1:numel(last_valid_before_invalid)
        
        % get last valid impulse before invalid impulses
        idx_last_valid  = last_valid_before_invalid(i);
        t_last_valid    = IMP_ONSET(idx_last_valid);
    
        % get next valid impulse after invalid impulses
        idx_next_valid  = idx_last_valid + ...
                          find(IMP_VALID(idx_last_valid+1:end),1,'first');
        t_next_valid    = IMP_ONSET(idx_next_valid);
        
        % add to array
        exclude_windows(i,:) = [t_last_valid t_next_valid];
    end

    % delete windows that are less then response latency (1200ms)
    too_short_idx = diff(exclude_windows, 1, 2) <= abs(latency_min * 1e3);
    exclude_windows(too_short_idx, :) = [];



    % ----- FILTER SEQUENCE VARIABLES -------------------------------------

    % exclude all invalid trials
    IMP_ONSET(~IMP_VALID)   = [];
    IMP_DIR(~IMP_VALID)     = [];


    % exclude responses during invalid impulses
    if ~isempty(exclude_windows)

        % preallocate
        exclude_resp_idx = false(size(RESPONSE_ONSET));
        
        % iteration over exclusion windows
        for i = 1:size(exclude_windows,1)
        
            exclude_resp_idx = exclude_resp_idx | ...
                (RESPONSE_ONSET >= exclude_windows(i,1) & ...
                 RESPONSE_ONSET <  exclude_windows(i,2));
        end

        RESPONSE_ONSET(exclude_resp_idx) = [];
    end



    % ----- GET DIRECTION AND LATENCY -------------------------------------

    % iteration over responses
    for resp = 1:numel(RESPONSE_ONSET)

        % latencies between impulse and response onsey
        latencies = IMP_ONSET - RESPONSE_ONSET(resp); 

        % extract impulses at latencies within analysis window
        imp_in_win = find(latencies >= latency_min * 1e3 & ...
                          latencies <= latency_max * 1e3);

        % count impulses according to latency and motion direction if 
        % consecutive impulse are within time window
        if numel(imp_in_win) >= 2

            % iterate over impulses of interest
            for i = 1:numel(imp_in_win)-1


                idx_1 = imp_in_win(i);    % first impulse index
                idx_2 = imp_in_win(i+1);  % second impulse index

                % direction bin
                dir_idx_1 = find(dir_bins == IMP_DIR(idx_1),1);
                dir_idx_2 = find(dir_bins == IMP_DIR(idx_2),1);

                % grouped direction bin
                dir_group_1 = dir_group(dir_idx_1);
                dir_group_2 = dir_group(dir_idx_2);

                % latency bin
                lag_idx_1 = discretize(latencies(idx_1), lag_bins * 1e3);


                % increase counter
                COUNT_ARRAY(lag_idx_1, dir_group_1, dir_group_2) = ...
                    COUNT_ARRAY(lag_idx_1, dir_group_1, dir_group_2) + 1;
            end
        end
    end
end



% ----- RESHAPE MATRIX ----------------------------------------------------

% ssign matrix rows to 2 dimensional array
for i = 1:size(COUNT_ARRAY,1)

    % get subset (8 x 8) at correspoding latency
    subset_row = squeeze(COUNT_ARRAY(i, :, :));

    % reshape to row vector (1 x 64)
    COUNT_MAT(i, :) = reshape(subset_row, 1, []);
end



% ----- NORMALIZATION -----------------------------------------------------

% normalize by total number of impulses at the same time lag
rowSum = sum(COUNT_MAT, 2, 'omitnan');
rowSum(rowSum == 0) = 1;            % prevent division by zero

COUNT_MAT   = COUNT_MAT ./ rowSum;  % probability for each impulse



% ----- SMOOTHING ---------------------------------------------------------

% low-pass Butterworth filter
bin_width   = diff(lag_bins) ./ 1e3;    % bin witdth in s
F.s         = 1 / bin_width(1);	        % sampling rate (Hz)
F.cut       = 4;           	            % cutoff frequency (Hz)
F.n         = 1;               	        % filter order
[b, a]      = butter(F.n, F.cut / (F.s / 2), 'low');

% zero-phase filtering
COUNT_MAT   = filtfilt(b, a, COUNT_MAT);



% ----- CREATE CORRELATION TABLE ------------------------------------------

% label for each direction sequence (64)
dir_labels = strings(1, nGroups^2);

idx = 1;
for d1 = (1:3:length(dir_bins))
    for d2 = (1:3:length(dir_bins))
        dir_labels(idx) = "Dir1_" + dir_bins(d1) + "_Dir2_" + dir_bins(d2);
        idx = idx + 1;
    end
end


% create correlation table
RMC_2_mat  = array2table(COUNT_MAT, ...
                         'VariableNames', dir_labels);

% add latency as first column
RMC_2_mat  = addvars(RMC_2_mat, (lag_bins + 25)', ...
                     'Before', 1, ...
                     'NewVariableNames', 'Latency');
end

