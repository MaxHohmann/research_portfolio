function [nHIT ,nFA, RT] = getPerformance(targets, responses, window)
% -------------------------------------------------------------------------
% GET PERFORMANCE
% -------------------------------------------------------------------------
% This function controlls whether each button response was a hit or a false 
% alarm. Outcomes of each responses are summarized for overall performance.
%
%
% INPUT
%       targets     : vector of timestamps (in µs) for target onsets
%       responses   : vector of timestamps (in µs) for response onsets
%       window      : vector of 2 values defining the upper and lower
%                     bound of the time window for hit responses
%
% OUTPUT
%       nHits       : total number of hits
%       nFA         : total number of False Alarms
%       RT          : vector containing all reaction times of hit responses
% -------------------------------------------------------------------------



% ----- EDGE CASES --------------------------------------------------------

% no targets and no responses -> no hits and no false alarms
if isempty(targets) && isempty(responses)
    nHIT    = 0;
    nFA     = 0;
    RT      = [];
    return;
end

% no targets -> all responses are false alarms
if isempty(targets)
    nHIT    = 0;
    nFA     = numel(responses);
    RT      = [];
    return;
end

% no responses -> all targets are missed
if isempty(responses)
    nHIT    = 0;
    nFA     = 0;
    RT      = [];
    return;
end



% ----- INITIALIZE VARIABLES ----------------------------------------------

nResp   = numel(responses);

hits    = false(1,nResp);
RT      = nan(1,nResp);
FA      = false(1,nResp);

% time limit for response window in us
tDelay_min = window(1) * 1e3;
tDelay_max = window(2) * 1e3;



% ----- GET OUTCOME FOR EACH RESPONSE -------------------------------------

for i = 1:nResp

    % time delay between response and targets
    tDelay = responses(i) - targets;
    
    % get targets that fall within response window
    resp_idx    = tDelay >= tDelay_min & ...
                  tDelay <= tDelay_max;


    % target within time window     -> Hit
    if sum(resp_idx) > 0

        hits(i) = true;
        FA(i)   = false;
        RT(i)   = tDelay(find(resp_idx,1,'first')) / 1e3;

    % no target within time window  -> False Alarm
    elseif sum(resp_idx) == 0

        hits(i) = false;
        FA(i)   = true;
        RT(i)   = nan;
    end
end



% ----- AGGREGATE PERFORMANCE ---------------------------------------------

nHIT    = sum(hits);
nFA     = sum(FA);
RT      = RT(~isnan(RT));


end